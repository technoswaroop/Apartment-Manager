using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data.Services;

public class MaintenanceManager
{
    private readonly AppDbContext _db;

    public MaintenanceManager(AppDbContext db)
    {
        _db = db;
    }

    public async Task SetMonthlyMaintenanceAsync(int flatId, decimal amount, int month, int year)
    {
        var charge = await _db.MaintenanceCharges
            .FirstOrDefaultAsync(c => c.FlatId == flatId && c.Month == month && c.Year == year);
        if (charge is null)
        {
            charge = new MaintenanceCharge
            {
                FlatId = flatId,
                Month = month,
                Year = year,
                StandardAmount = amount,
                AdjustedAmount = amount,
                Status = "Pending"
            };
            await _db.MaintenanceCharges.AddAsync(charge);
        }
        else
        {
            charge.StandardAmount = amount;
            charge.AdjustedAmount = Math.Max(0, amount - charge.PaidAmount);
        }
        await _db.SaveChangesAsync();
    }

    public async Task ProcessPaymentAsync(int flatId, decimal amount, DateTime paymentDate)
    {
        // Record payment
        await _db.PaymentRecords.AddAsync(new PaymentRecord
        {
            FlatId = flatId,
            Amount = amount,
            PaymentDate = paymentDate,
            PaymentType = "Maintenance",
            Reference = $"MTN-{paymentDate:yyyyMMddHHmmss}"
        });

        // Apply to most overdue pending charges first
        var charges = await _db.MaintenanceCharges
            .Where(c => c.FlatId == flatId)
            .OrderBy(c => c.Year).ThenBy(c => c.Month)
            .ToListAsync();

        decimal remaining = amount;
        foreach (var c in charges)
        {
            if (remaining <= 0) break;
            var due = (c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount;
            if (due <= 0) continue;

            var apply = Math.Min(remaining, due);
            c.PaidAmount += apply;
            remaining -= apply;
            if (c.PaidAmount >= (c.AdjustedAmount ?? c.StandardAmount))
            {
                c.Status = "Paid";
                c.PaymentDate = paymentDate;
            }
            else
            {
                c.Status = "Partial";
            }
        }

        await _db.SaveChangesAsync();
    }

    public async Task<List<MaintenanceCharge>> GetPendingMaintenanceAsync()
    {
        return await _db.MaintenanceCharges
            .Include(c => c.Flat)
            .Where(c => (c.AdjustedAmount ?? c.StandardAmount) > c.PaidAmount)
            .ToListAsync();
    }

    public async Task<decimal> CalculateAdjustedMaintenanceAsync(int flatId, int month, int year)
    {
        var charge = await _db.MaintenanceCharges.FirstOrDefaultAsync(c => c.FlatId == flatId && c.Month == month && c.Year == year);
        if (charge is null) return 0m;
        return (charge.AdjustedAmount ?? charge.StandardAmount) - charge.PaidAmount;
    }

    public async Task AdjustMaintenanceCreditAsync(int flatId, decimal creditAmount, int month, int year)
    {
        var charge = await _db.MaintenanceCharges.FirstOrDefaultAsync(c => c.FlatId == flatId && c.Month == month && c.Year == year);
        if (charge is null)
        {
            charge = new MaintenanceCharge
            {
                FlatId = flatId,
                Month = month,
                Year = year,
                StandardAmount = 0,
                AdjustedAmount = Math.Max(0, -creditAmount),
                Status = "Pending"
            };
            await _db.MaintenanceCharges.AddAsync(charge);
        }
        else
        {
            var currentAdjusted = charge.AdjustedAmount ?? charge.StandardAmount;
            charge.AdjustedAmount = Math.Max(0, currentAdjusted - creditAmount);
        }
        await _db.SaveChangesAsync();
    }
}