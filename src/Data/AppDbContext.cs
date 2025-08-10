using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data;

public class AppDbContext : DbContext
{
    public DbSet<Flat> Flats => Set<Flat>();
    public DbSet<MaintenanceCharge> MaintenanceCharges => Set<MaintenanceCharge>();
    public DbSet<RepairExpense> RepairExpenses => Set<RepairExpense>();
    public DbSet<ExpenseAllocation> ExpenseAllocations => Set<ExpenseAllocation>();
    public DbSet<PaymentRecord> PaymentRecords => Set<PaymentRecord>();
    public DbSet<AuditLog> AuditLogs => Set<AuditLog>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
    {
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Flat>(b =>
        {
            b.HasKey(x => x.FlatId);
            b.Property(x => x.FlatNumber).HasMaxLength(10).IsRequired();
            b.Property(x => x.OwnerName).HasMaxLength(100).IsRequired();
            b.Property(x => x.ContactDetails).HasMaxLength(200);
            b.Property(x => x.IsActive).HasDefaultValue(true);
        });

        modelBuilder.Entity<MaintenanceCharge>(b =>
        {
            b.HasKey(x => x.ChargeId);
            b.Property(x => x.StandardAmount).HasColumnType("decimal(10,2)");
            b.Property(x => x.AdjustedAmount).HasColumnType("decimal(10,2)");
            b.Property(x => x.PaidAmount).HasColumnType("decimal(10,2)");
            b.Property(x => x.Status).HasMaxLength(20).HasDefaultValue("Pending");
            b.HasOne(x => x.Flat)
                .WithMany(f => f.MaintenanceCharges)
                .HasForeignKey(x => x.FlatId)
                .OnDelete(DeleteBehavior.Cascade);
            b.HasIndex(x => new { x.FlatId, x.Month, x.Year }).IsUnique();
        });

        modelBuilder.Entity<RepairExpense>(b =>
        {
            b.HasKey(x => x.ExpenseId);
            b.Property(x => x.Description).IsRequired();
            b.Property(x => x.Amount).HasColumnType("decimal(10,2)");
            b.Property(x => x.Category).HasMaxLength(50);
            b.Property(x => x.IsSharedExpense).HasDefaultValue(true);
            b.Property(x => x.CreatedDate).HasDefaultValueSql("CURRENT_TIMESTAMP");
            b.HasOne(x => x.PaidByFlat)
                .WithMany()
                .HasForeignKey(x => x.PaidByFlatId)
                .OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<ExpenseAllocation>(b =>
        {
            b.HasKey(x => x.AllocationId);
            b.Property(x => x.AllocatedAmount).HasColumnType("decimal(10,2)");
            b.HasOne(x => x.Expense)
                .WithMany(e => e.Allocations)
                .HasForeignKey(x => x.ExpenseId)
                .OnDelete(DeleteBehavior.Cascade);
            b.HasOne(x => x.Flat)
                .WithMany(f => f.ExpenseAllocations)
                .HasForeignKey(x => x.FlatId)
                .OnDelete(DeleteBehavior.Cascade);
            b.HasIndex(x => new { x.ExpenseId, x.FlatId }).IsUnique();
        });

        modelBuilder.Entity<PaymentRecord>(b =>
        {
            b.HasKey(x => x.PaymentId);
            b.Property(x => x.Amount).HasColumnType("decimal(10,2)");
            b.Property(x => x.PaymentType).HasMaxLength(30);
            b.HasOne(x => x.Flat)
                .WithMany(f => f.PaymentRecords)
                .HasForeignKey(x => x.FlatId)
                .OnDelete(DeleteBehavior.Cascade);
            b.HasIndex(x => x.PaymentDate);
        });

        modelBuilder.Entity<AuditLog>(b =>
        {
            b.HasKey(x => x.AuditLogId);
            b.Property(x => x.TableName).HasMaxLength(100).IsRequired();
            b.Property(x => x.UserId).HasMaxLength(100).HasDefaultValue("system");
        });

        base.OnModelCreating(modelBuilder);
    }
}