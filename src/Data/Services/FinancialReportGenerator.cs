using ApartmentManager.Core.Models;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Data.Services;

public class FinancialReportGenerator
{
    private readonly AppDbContext _db;

    public FinancialReportGenerator(AppDbContext db)
    {
        _db = db;
    }

    public async Task<BalanceSheet> GenerateBalanceSheetAsync(int month, int year)
    {
        // Assets: Cash = total payments received up to period end
        var periodEnd = new DateTime(year, month, DateTime.DaysInMonth(year, month));
        var cash = await _db.PaymentRecords.Where(p => p.PaymentDate <= periodEnd).SumAsync(p => (decimal?)p.Amount) ?? 0m;

        // Liabilities: Outstanding maintenance up to period end
        var outstanding = await _db.MaintenanceCharges
            .Where(c => new DateTime(c.Year, c.Month, 1) <= periodEnd)
            .SumAsync(c => (decimal?)((c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount)) ?? 0m;

        var equity = cash - outstanding;
        return new BalanceSheet(cash, outstanding, equity);
    }

    public async Task<IncomeStatement> GenerateIncomeStatementAsync(DateTime startDate, DateTime endDate)
    {
        var income = await _db.PaymentRecords
            .Where(p => p.PaymentDate >= startDate && p.PaymentDate <= endDate)
            .SumAsync(p => (decimal?)p.Amount) ?? 0m;

        var expenses = await _db.RepairExpenses
            .Where(e => e.ExpenseDate >= startDate && e.ExpenseDate <= endDate)
            .SumAsync(e => (decimal?)e.Amount) ?? 0m;

        var net = income - expenses;
        return new IncomeStatement(income, expenses, net);
    }

    public async Task<CashFlowStatement> GenerateCashFlowReportAsync(DateTime startDate, DateTime endDate)
    {
        var inflows = await _db.PaymentRecords
            .Where(p => p.PaymentDate >= startDate && p.PaymentDate <= endDate)
            .SumAsync(p => (decimal?)p.Amount) ?? 0m;
        var outflows = await _db.RepairExpenses
            .Where(e => e.ExpenseDate >= startDate && e.ExpenseDate <= endDate)
            .SumAsync(e => (decimal?)e.Amount) ?? 0m;
        return new CashFlowStatement(inflows, outflows, inflows - outflows);
    }

    public async Task ExportToCsvAsync(ReportType reportType, DateTime period, string outputPath)
    {
        switch (reportType)
        {
            case ReportType.BalanceSheet:
                var bs = await GenerateBalanceSheetAsync(period.Month, period.Year);
                await File.WriteAllTextAsync(outputPath, $"Assets,Liabilities,Equity\n{bs.TotalAssets:0.00},{bs.TotalLiabilities:0.00},{bs.Equity:0.00}\n");
                break;
            case ReportType.IncomeStatement:
                var isr = await GenerateIncomeStatementAsync(new DateTime(period.Year, period.Month, 1), new DateTime(period.Year, period.Month, DateTime.DaysInMonth(period.Year, period.Month)));
                await File.WriteAllTextAsync(outputPath, $"Income,Expenses,Net\n{isr.TotalIncome:0.00},{isr.TotalExpenses:0.00},{isr.NetIncome:0.00}\n");
                break;
            case ReportType.CashFlow:
                var cfr = await GenerateCashFlowReportAsync(new DateTime(period.Year, period.Month, 1), new DateTime(period.Year, period.Month, DateTime.DaysInMonth(period.Year, period.Month)));
                await File.WriteAllTextAsync(outputPath, $"Inflows,Outflows,Net\n{cfr.Inflows:0.00},{cfr.Outflows:0.00},{cfr.NetCashFlow:0.00}\n");
                break;
        }
    }
}