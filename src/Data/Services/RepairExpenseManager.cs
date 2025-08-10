using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data.Services;

public class RepairExpenseManager
{
    private readonly AppDbContext _db;

    public RepairExpenseManager(AppDbContext db)
    {
        _db = db;
    }

    public async Task<RepairExpense> AddRepairExpenseAsync(string description, decimal amount, int? paidByFlatId, string? category = null, DateTime? expenseDate = null)
    {
        var expense = new RepairExpense
        {
            Description = description,
            Amount = amount,
            PaidByFlatId = paidByFlatId,
            ExpenseDate = expenseDate ?? DateTime.Today,
            Category = category,
            IsSharedExpense = true
        };
        await _db.RepairExpenses.AddAsync(expense);
        await _db.SaveChangesAsync();
        return expense;
    }

    public async Task AllocateExpenseToFlatsAsync(int expenseId, Dictionary<int, decimal> allocations)
    {
        var expense = await _db.RepairExpenses.FirstAsync(e => e.ExpenseId == expenseId);
        // Remove previous allocations if any
        var existing = _db.ExpenseAllocations.Where(a => a.ExpenseId == expenseId);
        _db.ExpenseAllocations.RemoveRange(existing);

        foreach (var kvp in allocations)
        {
            _db.ExpenseAllocations.Add(new ExpenseAllocation
            {
                ExpenseId = expenseId,
                FlatId = kvp.Key,
                AllocatedAmount = kvp.Value
            });
        }

        await _db.SaveChangesAsync();
    }

    public async Task ProcessRepairPaymentByOwnerAsync(int flatId, decimal repairAmount, string description)
    {
        var expense = await AddRepairExpenseAsync(description, repairAmount, flatId);
        var perFlatAllocation = Math.Round(repairAmount / 7m, 2, MidpointRounding.AwayFromZero);

        // Distribute to all 7 flats equally
        var flatIds = await _db.Flats.Select(f => f.FlatId).OrderBy(id => id).ToListAsync();
        if (flatIds.Count != 7)
        {
            // In case flats not seeded, still proceed with available flats
        }
        var allocations = new Dictionary<int, decimal>();
        foreach (var id in flatIds)
        {
            allocations[id] = perFlatAllocation;
        }
        await AllocateExpenseToFlatsAsync(expense.ExpenseId, allocations);

        // Credit the payer by their own allocation against earliest available maintenance charge
        var earliestCharge = await _db.MaintenanceCharges
            .Where(c => c.FlatId == flatId)
            .OrderBy(c => c.Year).ThenBy(c => c.Month)
            .FirstOrDefaultAsync();
        var maintenance = new MaintenanceManager(_db);
        if (earliestCharge is not null)
        {
            await maintenance.AdjustMaintenanceCreditAsync(flatId, perFlatAllocation, earliestCharge.Month, earliestCharge.Year);
        }
        else
        {
            var today = DateTime.Today;
            await maintenance.AdjustMaintenanceCreditAsync(flatId, perFlatAllocation, today.Month, today.Year);
        }
    }

    public async Task AdjustMaintenanceForAdvancedPaymentAsync(int flatId, decimal advanceAmount)
    {
        var today = DateTime.Today;
        var maintenance = new MaintenanceManager(_db);
        await maintenance.AdjustMaintenanceCreditAsync(flatId, advanceAmount, today.Month, today.Year);
    }
}