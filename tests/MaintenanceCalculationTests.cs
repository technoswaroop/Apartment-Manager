using ApartmentManager.Core.Models;
using ApartmentManager.Data;
using ApartmentManager.Data.Services;
using Microsoft.EntityFrameworkCore;
using Xunit;

namespace ApartmentManager.Tests;

public class MaintenanceCalculationTests
{
    private static AppDbContext CreateInMemoryDb()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(Guid.NewGuid().ToString())
            .Options;
        var db = new AppDbContext(options);
        // Seed flats
        for (int i = 1; i <= 7; i++)
        {
            db.Flats.Add(new Flat { FlatNumber = $"F{i}", OwnerName = $"Owner {i}" });
        }
        db.SaveChanges();
        return db;
    }

    [Fact]
    public async Task CalculateAdjustedMaintenance_WhenOwnerPaysRepair_ShouldReduceMaintenance()
    {
        await using var db = CreateInMemoryDb();
        var maintenance = new MaintenanceManager(db);
        var repairs = new RepairExpenseManager(db);

        // Setup monthly maintenance for one flat
        await maintenance.SetMonthlyMaintenanceAsync(1, 1000m, 1, 2025);

        // Owner 1 pays a repair shared by all -> credit equal to 1/7
        await repairs.ProcessRepairPaymentByOwnerAsync(1, 700m, "Gate repair");

        var adjusted = await maintenance.CalculateAdjustedMaintenanceAsync(1, 1, 2025);
        Assert.Equal(900m, Math.Round(adjusted, 2));
    }

    [Fact]
    public async Task GenerateDefaulterList_WithPendingPayments_ShouldReturnCorrectDefaulters()
    {
        await using var db = CreateInMemoryDb();
        var maintenance = new MaintenanceManager(db);
        var defaulters = new DefaulterTracker(db);

        // Flat 1 and 2 have charges but only 1 pays partially
        await maintenance.SetMonthlyMaintenanceAsync(1, 1000m, 1, 2025);
        await maintenance.SetMonthlyMaintenanceAsync(2, 1000m, 1, 2025);
        await maintenance.ProcessPaymentAsync(1, 400m, DateTime.Today);

        var list = await defaulters.GetCurrentDefaultersAsync();
        var f1 = list.Single(d => d.FlatId == 1);
        var f2 = list.Single(d => d.FlatId == 2);

        Assert.Equal(600m, Math.Round(f1.OutstandingAmount, 2));
        Assert.Equal(1000m, Math.Round(f2.OutstandingAmount, 2));
    }
}