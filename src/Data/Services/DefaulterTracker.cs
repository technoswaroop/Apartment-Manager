using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data.Services;

public class DefaulterTracker
{
    private readonly AppDbContext _db;

    public DefaulterTracker(AppDbContext db)
    {
        _db = db;
    }

    public async Task<List<DefaulterInfo>> GetCurrentDefaultersAsync()
    {
        var list = await _db.MaintenanceCharges
            .Include(c => c.Flat)
            .GroupBy(c => c.Flat!)
            .Select(g => new
            {
                Flat = g.Key,
                Outstanding = g.Sum(c => (c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount),
                PendingMonths = g.Count(c => (c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount > 0)
            })
            .Where(x => x.Outstanding > 0)
            .OrderByDescending(x => x.Outstanding)
            .ToListAsync();

        return list.Select(x => new DefaulterInfo
        {
            FlatId = x.Flat.FlatId,
            FlatNumber = x.Flat.FlatNumber,
            OwnerName = x.Flat.OwnerName,
            ContactDetails = x.Flat.ContactDetails,
            OutstandingAmount = Math.Round(x.Outstanding, 2, MidpointRounding.AwayFromZero),
            PendingMonths = x.PendingMonths
        }).ToList();
    }

    public async Task<DefaulterInfo?> GetFlatDetailsAsync(int flatId)
    {
        var flat = await _db.Flats.FirstOrDefaultAsync(f => f.FlatId == flatId);
        if (flat is null) return null;

        var charges = await _db.MaintenanceCharges.Where(c => c.FlatId == flatId).ToListAsync();
        var outstanding = charges.Sum(c => (c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount);
        var pendingMonths = charges.Count(c => (c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount > 0);

        return new DefaulterInfo
        {
            FlatId = flat.FlatId,
            FlatNumber = flat.FlatNumber,
            OwnerName = flat.OwnerName,
            ContactDetails = flat.ContactDetails,
            OutstandingAmount = Math.Round(outstanding, 2, MidpointRounding.AwayFromZero),
            PendingMonths = pendingMonths
        };
    }

    public async Task GenerateDefaulterReportAsync(DateTime asOfDate, string outputPath)
    {
        var defaulters = await GetCurrentDefaultersAsync();
        using var writer = new StreamWriter(outputPath);
        await writer.WriteLineAsync($"Defaulter Report as of {asOfDate:dd-MMM-yyyy}");
        await writer.WriteLineAsync("Flat,Owner,Contact,Outstanding,PendingMonths");
        foreach (var d in defaulters)
        {
            await writer.WriteLineAsync($"{d.FlatNumber},{d.OwnerName},{d.ContactDetails},{d.OutstandingAmount:0.00},{d.PendingMonths}");
        }
    }
}