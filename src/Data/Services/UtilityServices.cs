using System.Globalization;
using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data.Services;

public class CurrencyManager
{
    private const string BaseCurrency = "INR";

    public string FormatCurrency(decimal amount)
    {
        var culture = new CultureInfo("en-IN");
        return string.Create(culture, $"{amount:C}").Replace("Rs.", "₹");
    }

    public void SetCurrencyPreferences()
    {
        CultureInfo.CurrentCulture = new CultureInfo("en-IN");
        CultureInfo.CurrentUICulture = new CultureInfo("en-IN");
    }
}

public class AuditManager
{
    private readonly AppDbContext _db;
    public AuditManager(AppDbContext db) { _db = db; }

    public async Task LogChangeAsync(string tableName, int recordId, string changes, string userId)
    {
        await _db.AuditLogs.AddAsync(new AuditLog
        {
            TableName = tableName,
            RecordId = recordId,
            Changes = changes,
            UserId = userId,
            ChangedAt = DateTime.UtcNow
        });
        await _db.SaveChangesAsync();
    }

    public async Task<List<AuditLog>> GetChangeHistoryAsync(string tableName, int recordId)
    {
        return await _db.AuditLogs
            .Where(a => a.TableName == tableName && a.RecordId == recordId)
            .OrderByDescending(a => a.ChangedAt)
            .ToListAsync();
    }
}

public class LocalDataManager
{
    private readonly DbContextOptions<AppDbContext> _options;

    public LocalDataManager(string databasePath)
    {
        var builder = new DbContextOptionsBuilder<AppDbContext>();
        builder.UseSqlite($"Data Source={databasePath}");
        _options = builder.Options;
    }

    public AppDbContext CreateDbContext() => new AppDbContext(_options);

    public async Task InitializeDatabaseAsync()
    {
        await using var db = CreateDbContext();
        await db.Database.MigrateAsync();

        // Seed 7 flats if not exists
        if (!await db.Flats.AnyAsync())
        {
            for (int i = 1; i <= 7; i++)
            {
                db.Flats.Add(new Flat
                {
                    FlatNumber = $"F{i}",
                    OwnerName = $"Owner {i}",
                    ContactDetails = $"+91-90000000{i}"
                });
            }
            await db.SaveChangesAsync();
        }

        // Indexes and maintenance are handled by EF migrations
    }

    public async Task PerformMaintenanceAsync()
    {
        await using var db = CreateDbContext();
        await db.Database.ExecuteSqlRawAsync("VACUUM");
        await db.Database.ExecuteSqlRawAsync("PRAGMA optimize");
    }
}

public enum BackupFrequency { Daily, Weekly, Monthly }

public class BackupManager
{
    private readonly string _databasePath;

    public BackupManager(string databasePath)
    {
        _databasePath = databasePath;
    }

    public void CreateBackup(string backupPath)
    {
        Directory.CreateDirectory(Path.GetDirectoryName(backupPath)!);
        File.Copy(_databasePath, backupPath, overwrite: true);
    }

    public void RestoreFromBackup(string backupFile)
    {
        File.Copy(backupFile, _databasePath, overwrite: true);
    }

    public bool VerifyBackupIntegrity(string backupFile)
    {
        return File.Exists(backupFile) && new FileInfo(backupFile).Length > 0;
    }

    public void ScheduleAutomaticBackups(BackupFrequency frequency)
    {
        // Stub for Windows Task Scheduler integration in WPF app
    }
}