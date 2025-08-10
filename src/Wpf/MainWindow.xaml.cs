using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using ApartmentManager.Data;
using ApartmentManager.Data.Services;
using Microsoft.EntityFrameworkCore;

namespace ApartmentManager.Wpf;

public partial class MainWindow : Window
{
    private readonly string _dbPath;
    private readonly LocalDataManager _local;
    private AppDbContext _db = null!;

    public MainWindow()
    {
        InitializeComponent();
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        var appFolder = Path.Combine(appData, "ApartmentManager");
        Directory.CreateDirectory(appFolder);
        _dbPath = Path.Combine(appFolder, "apartment.db");
        _local = new LocalDataManager(_dbPath);
        Loaded += MainWindow_Loaded;

        BtnSetMaintenance.Click += async (_, __) => await SetMaintenanceAsync();
        BtnRecordPayment.Click += async (_, __) => await RecordPaymentAsync();
        BtnExportReport.Click += async (_, __) => await ExportOverviewAsync();
        BtnAddRepair.Click += async (_, __) => await AddRepairAsync();
        BtnExportBalanceSheet.Click += async (_, __) => await ExportBalanceSheetAsync();
        BtnExportIncome.Click += async (_, __) => await ExportIncomeAsync();
        BtnExportCashFlow.Click += async (_, __) => await ExportCashFlowAsync();
        BtnCreateBackup.Click += (_, __) => CreateBackup();
        BtnRestoreBackup.Click += (_, __) => RestoreBackup();
    }

    private async void MainWindow_Loaded(object sender, RoutedEventArgs e)
    {
        await _local.InitializeDatabaseAsync();
        _db = _local.CreateDbContext();
        await RefreshUiAsync();
        await LoadPaidByComboAsync();
    }

    private async Task RefreshUiAsync()
    {
        MaintenanceGrid.ItemsSource = await _db.MaintenanceCharges.Include(c => c.Flat).OrderByDescending(c => c.Year).ThenByDescending(c => c.Month).ToListAsync();
        var defaulters = new DefaulterTracker(_db);
        DefaultersGrid.ItemsSource = await defaulters.GetCurrentDefaultersAsync();

        var totalCollected = await _db.PaymentRecords.SumAsync(p => (decimal?)p.Amount) ?? 0m;
        var totalPending = await _db.MaintenanceCharges.SumAsync(c => (decimal?)((c.AdjustedAmount ?? c.StandardAmount) - c.PaidAmount)) ?? 0m;
        var currency = new CurrencyManager();
        TotalCollectedText.Text = $"Total Collected: {currency.FormatCurrency(totalCollected)}";
        TotalPendingText.Text = $"Total Pending: {currency.FormatCurrency(totalPending)}";
        DefaultersText.Text = $"Defaulters: {(await defaulters.GetCurrentDefaultersAsync()).Count}";
    }

    private async Task LoadPaidByComboAsync()
    {
        var flats = await _db.Flats.OrderBy(f => f.FlatNumber).ToListAsync();
        PaidByFlatCombo.ItemsSource = flats;
        PaidByFlatCombo.DisplayMemberPath = "FlatNumber";
        PaidByFlatCombo.SelectedValuePath = "FlatId";
        if (flats.Count > 0) PaidByFlatCombo.SelectedIndex = 0;
    }

    private async Task SetMaintenanceAsync()
    {
        var dlg = new SimpleInputs("Set Maintenance", new[] { "Flat ID", "Amount", "Month", "Year" });
        if (dlg.ShowDialog() == true)
        {
            var flatId = int.Parse(dlg.Values[0]);
            var amount = decimal.Parse(dlg.Values[1]);
            var month = int.Parse(dlg.Values[2]);
            var year = int.Parse(dlg.Values[3]);
            var svc = new MaintenanceManager(_db);
            await svc.SetMonthlyMaintenanceAsync(flatId, amount, month, year);
            await RefreshUiAsync();
        }
    }

    private async Task RecordPaymentAsync()
    {
        var dlg = new SimpleInputs("Record Payment", new[] { "Flat ID", "Amount" });
        if (dlg.ShowDialog() == true)
        {
            var flatId = int.Parse(dlg.Values[0]);
            var amount = decimal.Parse(dlg.Values[1]);
            var svc = new MaintenanceManager(_db);
            await svc.ProcessPaymentAsync(flatId, amount, DateTime.Today);
            await RefreshUiAsync();
        }
    }

    private async Task AddRepairAsync()
    {
        if (PaidByFlatCombo.SelectedValue is int flatId && decimal.TryParse(RepairAmount.Text, out var amt))
        {
            var svc = new RepairExpenseManager(_db);
            await svc.ProcessRepairPaymentByOwnerAsync(flatId, amt, RepairDescription.Text);
            RepairDescription.Text = string.Empty;
            RepairAmount.Text = string.Empty;
            await RefreshUiAsync();
        }
        else
        {
            MessageBox.Show("Please select a flat and enter a valid amount.");
        }
    }

    private async Task ExportOverviewAsync()
    {
        var sfd = new Microsoft.Win32.SaveFileDialog { Filter = "CSV files (*.csv)|*.csv", FileName = $"Defaulters-{DateTime.Today:yyyyMMdd}.csv" };
        if (sfd.ShowDialog() == true)
        {
            var defaulters = new DefaulterTracker(_db);
            await defaulters.GenerateDefaulterReportAsync(DateTime.Today, sfd.FileName);
            MessageBox.Show("Exported.");
        }
    }

    private async Task ExportBalanceSheetAsync()
    {
        var sfd = new Microsoft.Win32.SaveFileDialog { Filter = "CSV files (*.csv)|*.csv", FileName = $"BalanceSheet-{DateTime.Today:yyyyMM}.csv" };
        if (sfd.ShowDialog() == true)
        {
            var rep = new FinancialReportGenerator(_db);
            await rep.ExportToCsvAsync(Core.Models.ReportType.BalanceSheet, DateTime.Today, sfd.FileName);
            MessageBox.Show("Exported.");
        }
    }

    private async Task ExportIncomeAsync()
    {
        var sfd = new Microsoft.Win32.SaveFileDialog { Filter = "CSV files (*.csv)|*.csv", FileName = $"Income-{DateTime.Today:yyyyMM}.csv" };
        if (sfd.ShowDialog() == true)
        {
            var rep = new FinancialReportGenerator(_db);
            await rep.ExportToCsvAsync(Core.Models.ReportType.IncomeStatement, DateTime.Today, sfd.FileName);
            MessageBox.Show("Exported.");
        }
    }

    private async Task ExportCashFlowAsync()
    {
        var sfd = new Microsoft.Win32.SaveFileDialog { Filter = "CSV files (*.csv)|*.csv", FileName = $"CashFlow-{DateTime.Today:yyyyMM}.csv" };
        if (sfd.ShowDialog() == true)
        {
            var rep = new FinancialReportGenerator(_db);
            await rep.ExportToCsvAsync(Core.Models.ReportType.CashFlow, DateTime.Today, sfd.FileName);
            MessageBox.Show("Exported.");
        }
    }

    private void CreateBackup()
    {
        var sfd = new Microsoft.Win32.SaveFileDialog { Filter = "DB files (*.db)|*.db", FileName = $"apartment-backup-{DateTime.Now:yyyyMMddHHmm}.db" };
        if (sfd.ShowDialog() == true)
        {
            var backup = new BackupManager(_dbPath);
            backup.CreateBackup(sfd.FileName);
            MessageBox.Show("Backup created.");
        }
    }

    private void RestoreBackup()
    {
        var ofd = new Microsoft.Win32.OpenFileDialog { Filter = "DB files (*.db)|*.db" };
        if (ofd.ShowDialog() == true)
        {
            var backup = new BackupManager(_dbPath);
            backup.RestoreFromBackup(ofd.FileName);
            MessageBox.Show("Restored. Please restart the app.");
        }
    }
}

public class SimpleInputs : Window
{
    private readonly System.Collections.Generic.List<System.Windows.Controls.TextBox> _boxes = new();
    public System.Collections.Generic.List<string> Values => _boxes.Select(b => b.Text).ToList();

    public SimpleInputs(string title, string[] labels)
    {
        Title = title;
        Width = 400;
        Height = 200;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        var panel = new System.Windows.Controls.StackPanel { Margin = new Thickness(10) };
        foreach (var l in labels)
        {
            panel.Children.Add(new System.Windows.Controls.TextBlock { Text = l });
            var box = new System.Windows.Controls.TextBox { Margin = new Thickness(0, 0, 0, 6) };
            panel.Children.Add(box);
            _boxes.Add(box);
        }
        var btn = new System.Windows.Controls.Button { Content = "OK", Width = 80, HorizontalAlignment = HorizontalAlignment.Right };
        btn.Click += (_, __) => { DialogResult = true; Close(); };
        panel.Children.Add(btn);
        Content = panel;
    }
}