using System;
using System.IO;
using System.Threading.Tasks;
using System.Windows;
using ApartmentManager.Data.Services;

namespace ApartmentManager.Wpf;

public partial class App : Application
{
    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        var appData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        var appFolder = Path.Combine(appData, "ApartmentManager");
        Directory.CreateDirectory(appFolder);
        var dbPath = Path.Combine(appFolder, "apartment.db");

        var localData = new LocalDataManager(dbPath);
        await localData.InitializeDatabaseAsync();
        await localData.PerformMaintenanceAsync();

        var currency = new CurrencyManager();
        currency.SetCurrencyPreferences();
    }
}