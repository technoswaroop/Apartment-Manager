namespace ApartmentManager.Core.Models;

public class Flat
{
    public int FlatId { get; set; }
    public string FlatNumber { get; set; } = string.Empty;
    public string OwnerName { get; set; } = string.Empty;
    public string? ContactDetails { get; set; }
    public bool IsActive { get; set; } = true;

    public List<MaintenanceCharge> MaintenanceCharges { get; set; } = new();
    public List<ExpenseAllocation> ExpenseAllocations { get; set; } = new();
    public List<PaymentRecord> PaymentRecords { get; set; } = new();
}

public class MaintenanceCharge
{
    public int ChargeId { get; set; }
    public int FlatId { get; set; }
    public int Month { get; set; }
    public int Year { get; set; }
    public decimal StandardAmount { get; set; }
    public decimal? AdjustedAmount { get; set; }
    public decimal PaidAmount { get; set; }
    public DateTime? PaymentDate { get; set; }
    public string Status { get; set; } = "Pending"; // Pending, Partial, Paid
    public string? Remarks { get; set; }

    public Flat? Flat { get; set; }
}

public class RepairExpense
{
    public int ExpenseId { get; set; }
    public string Description { get; set; } = string.Empty;
    public decimal Amount { get; set; }
    public DateTime ExpenseDate { get; set; }
    public int? PaidByFlatId { get; set; }
    public string? Category { get; set; }
    public bool IsSharedExpense { get; set; } = true;
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;

    public Flat? PaidByFlat { get; set; }
    public List<ExpenseAllocation> Allocations { get; set; } = new();
}

public class ExpenseAllocation
{
    public int AllocationId { get; set; }
    public int ExpenseId { get; set; }
    public int FlatId { get; set; }
    public decimal AllocatedAmount { get; set; }

    public RepairExpense? Expense { get; set; }
    public Flat? Flat { get; set; }
}

public class PaymentRecord
{
    public int PaymentId { get; set; }
    public int FlatId { get; set; }
    public decimal Amount { get; set; }
    public DateTime PaymentDate { get; set; }
    public string PaymentType { get; set; } = string.Empty; // UPI, Cash, Bank Transfer
    public string? Reference { get; set; }
    public string? Remarks { get; set; }

    public Flat? Flat { get; set; }
}

public class AuditLog
{
    public int AuditLogId { get; set; }
    public string TableName { get; set; } = string.Empty;
    public int RecordId { get; set; }
    public string Changes { get; set; } = string.Empty;
    public string UserId { get; set; } = "system";
    public DateTime ChangedAt { get; set; } = DateTime.UtcNow;
}

public class DefaulterInfo
{
    public int FlatId { get; set; }
    public string FlatNumber { get; set; } = string.Empty;
    public string OwnerName { get; set; } = string.Empty;
    public string? ContactDetails { get; set; }
    public decimal OutstandingAmount { get; set; }
    public int PendingMonths { get; set; }
}

public record BalanceSheet(decimal TotalAssets, decimal TotalLiabilities, decimal Equity);

public record IncomeStatement(decimal TotalIncome, decimal TotalExpenses, decimal NetIncome);

public record CashFlowStatement(decimal Inflows, decimal Outflows, decimal NetCashFlow);

public enum ReportType
{
    BalanceSheet,
    IncomeStatement,
    CashFlow
}