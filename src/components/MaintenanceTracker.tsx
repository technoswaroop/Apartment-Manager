import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CalendarDays, DollarSign, Users, AlertTriangle, TrendingUp, Building } from "lucide-react";

interface FlatOwner {
  flatNumber: string;
  ownerName: string;
  contactInfo: string;
  notes: string;
}

interface Payment {
  id: string;
  flatNumber: string;
  month: string;
  year: string;
  datePaid: string;
  amountPaid: number;
  paymentMethod: string;
}

interface Expense {
  id: string;
  date: string;
  description: string;
  totalCost: number;
  vendor: string;
  paidBy: string;
  splitType: "equal" | "custom";
}

const MaintenanceTracker = () => {
  const [monthlyCharge] = useState(100);
  const [currentTab, setCurrentTab] = useState("dashboard");
  
  // Sample data
  const [flatOwners] = useState<FlatOwner[]>([
    { flatNumber: "Flat 1", ownerName: "John Smith", contactInfo: "john@email.com | +1234567890", notes: "Prefers bank transfer" },
    { flatNumber: "Flat 2", ownerName: "Sarah Johnson", contactInfo: "sarah@email.com | +1234567891", notes: "Usually pays on 1st" },
    { flatNumber: "Flat 3", ownerName: "Mike Wilson", contactInfo: "mike@email.com | +1234567892", notes: "Cash payments only" },
    { flatNumber: "Flat 4", ownerName: "Emma Davis", contactInfo: "emma@email.com | +1234567893", notes: "New tenant" },
    { flatNumber: "Flat 5", ownerName: "David Brown", contactInfo: "david@email.com | +1234567894", notes: "Building committee member" },
    { flatNumber: "Flat 6", ownerName: "Lisa Anderson", contactInfo: "lisa@email.com | +1234567895", notes: "Frequent traveler" },
    { flatNumber: "Flat 7", ownerName: "Tom Garcia", contactInfo: "tom@email.com | +1234567896", notes: "Senior citizen" }
  ]);

  const [payments] = useState<Payment[]>([
    { id: "1", flatNumber: "Flat 1", month: "January", year: "2024", datePaid: "2024-01-05", amountPaid: 100, paymentMethod: "Bank Transfer" },
    { id: "2", flatNumber: "Flat 2", month: "January", year: "2024", datePaid: "2024-01-03", amountPaid: 100, paymentMethod: "Cash" },
    { id: "3", flatNumber: "Flat 3", month: "January", year: "2024", datePaid: "2024-01-10", amountPaid: 100, paymentMethod: "Cash" },
    { id: "4", flatNumber: "Flat 1", month: "February", year: "2024", datePaid: "2024-02-05", amountPaid: 100, paymentMethod: "Bank Transfer" },
    { id: "5", flatNumber: "Flat 2", month: "February", year: "2024", datePaid: "2024-02-03", amountPaid: 100, paymentMethod: "Cash" },
  ]);

  const [expenses] = useState<Expense[]>([
    { id: "1", date: "2024-01-15", description: "Elevator maintenance", totalCost: 350, vendor: "ElevoTech", paidBy: "Flat 5", splitType: "equal" },
    { id: "2", date: "2024-01-20", description: "Common area cleaning supplies", totalCost: 140, vendor: "CleanCorp", paidBy: "Building Fund", splitType: "equal" },
    { id: "3", date: "2024-02-10", description: "Plumbing repair", totalCost: 280, vendor: "PlumbPro", paidBy: "Flat 3", splitType: "equal" },
  ]);

  const getPaymentStatus = (flatNumber: string, month: string, year: string) => {
    const payment = payments.find(p => p.flatNumber === flatNumber && p.month === month && p.year === year);
    if (!payment) return "pending";
    if (payment.amountPaid >= monthlyCharge) return "paid";
    return "partial";
  };

  const getDefaulters = () => {
    return flatOwners.filter(flat => {
      const janPayment = getPaymentStatus(flat.flatNumber, "January", "2024");
      const febPayment = getPaymentStatus(flat.flatNumber, "February", "2024");
      return janPayment === "pending" || febPayment === "pending";
    });
  };

  const getTotalCollected = () => {
    return payments.reduce((total, payment) => total + payment.amountPaid, 0);
  };

  const getTotalExpenses = () => {
    return expenses.reduce((total, expense) => total + expense.totalCost, 0);
  };

  const getNetBalance = () => {
    return getTotalCollected() - getTotalExpenses();
  };

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Building className="h-8 w-8 text-primary" />
            <h1 className="text-3xl font-bold text-foreground">Maintenance Tracker</h1>
          </div>
          <p className="text-muted-foreground">7-Flat Residential Building Management System</p>
        </div>

        <Tabs value={currentTab} onValueChange={setCurrentTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="owners" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Flat Owners
            </TabsTrigger>
            <TabsTrigger value="payments" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Payments
            </TabsTrigger>
            <TabsTrigger value="expenses" className="flex items-center gap-2">
              <CalendarDays className="h-4 w-4" />
              Expenses
            </TabsTrigger>
            <TabsTrigger value="reports" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Reports
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Key Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Collected</CardTitle>
                  <DollarSign className="h-4 w-4 text-success" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-success">${getTotalCollected()}</div>
                  <p className="text-xs text-muted-foreground">From all payments</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
                  <CalendarDays className="h-4 w-4 text-destructive" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-destructive">${getTotalExpenses()}</div>
                  <p className="text-xs text-muted-foreground">All building expenses</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Net Balance</CardTitle>
                  <TrendingUp className="h-4 w-4 text-primary" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${getNetBalance() >= 0 ? 'text-success' : 'text-destructive'}`}>
                    ${getNetBalance()}
                  </div>
                  <p className="text-xs text-muted-foreground">Receipts - Expenses</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Defaulters</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-warning" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-warning">{getDefaulters().length}</div>
                  <p className="text-xs text-muted-foreground">Pending payments</p>
                </CardContent>
              </Card>
            </div>

            {/* Quick Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Payment Status Overview */}
              <Card>
                <CardHeader>
                  <CardTitle>Payment Status - February 2024</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {flatOwners.map((flat) => {
                      const status = getPaymentStatus(flat.flatNumber, "February", "2024");
                      return (
                        <div key={flat.flatNumber} className="flex items-center justify-between">
                          <span className="font-medium">{flat.flatNumber}</span>
                          <Badge 
                            variant={status === "paid" ? "default" : status === "partial" ? "secondary" : "destructive"}
                            className={
                              status === "paid" ? "bg-success text-success-foreground" :
                              status === "partial" ? "bg-warning text-warning-foreground" :
                              "bg-destructive text-destructive-foreground"
                            }
                          >
                            {status === "paid" ? "Paid" : status === "partial" ? "Partial" : "Pending"}
                          </Badge>
                        </div>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>

              {/* Defaulters List */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-warning" />
                    Defaulters Alert
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {getDefaulters().length === 0 ? (
                      <p className="text-muted-foreground">No pending payments!</p>
                    ) : (
                      getDefaulters().map((flat) => (
                        <div key={flat.flatNumber} className="p-3 bg-warning-light rounded-lg">
                          <div className="font-medium">{flat.flatNumber} - {flat.ownerName}</div>
                          <div className="text-sm text-muted-foreground">{flat.contactInfo.split(' | ')[0]}</div>
                          <div className="text-sm text-warning font-medium">Outstanding payment pending</div>
                        </div>
                      ))
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Flat Owners Tab */}
          <TabsContent value="owners" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Flat Owner Information</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Flat Number</TableHead>
                      <TableHead>Owner Name</TableHead>
                      <TableHead>Contact Info</TableHead>
                      <TableHead>Notes</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {flatOwners.map((flat) => (
                      <TableRow key={flat.flatNumber}>
                        <TableCell className="font-medium">{flat.flatNumber}</TableCell>
                        <TableCell>{flat.ownerName}</TableCell>
                        <TableCell>{flat.contactInfo}</TableCell>
                        <TableCell>{flat.notes}</TableCell>
                        <TableCell>
                          <Button variant="outline" size="sm">Edit</Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Payments Tab */}
          <TabsContent value="payments" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Monthly Payments</h2>
              <div className="flex items-center gap-4">
                <Label>Monthly Charge: ${monthlyCharge}</Label>
                <Button>Add Payment</Button>
              </div>
            </div>
            
            <Card>
              <CardContent className="pt-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Flat</TableHead>
                      <TableHead>Month/Year</TableHead>
                      <TableHead>Date Paid</TableHead>
                      <TableHead>Amount</TableHead>
                      <TableHead>Method</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {payments.map((payment) => (
                      <TableRow key={payment.id}>
                        <TableCell className="font-medium">{payment.flatNumber}</TableCell>
                        <TableCell>{payment.month} {payment.year}</TableCell>
                        <TableCell>{payment.datePaid}</TableCell>
                        <TableCell>${payment.amountPaid}</TableCell>
                        <TableCell>{payment.paymentMethod}</TableCell>
                        <TableCell>
                          <Badge className="bg-success text-success-foreground">Paid</Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Expenses Tab */}
          <TabsContent value="expenses" className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Building Expenses</h2>
              <Button>Add Expense</Button>
            </div>
            
            <Card>
              <CardContent className="pt-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead>Total Cost</TableHead>
                      <TableHead>Vendor</TableHead>
                      <TableHead>Paid By</TableHead>
                      <TableHead>Per Flat Share</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {expenses.map((expense) => (
                      <TableRow key={expense.id}>
                        <TableCell>{expense.date}</TableCell>
                        <TableCell className="font-medium">{expense.description}</TableCell>
                        <TableCell>${expense.totalCost}</TableCell>
                        <TableCell>{expense.vendor}</TableCell>
                        <TableCell>{expense.paidBy}</TableCell>
                        <TableCell>${(expense.totalCost / 7).toFixed(2)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Financial Summary Report</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-success-light rounded-lg">
                    <h3 className="font-semibold text-success">Total Income</h3>
                    <p className="text-2xl font-bold text-success">${getTotalCollected()}</p>
                  </div>
                  <div className="p-4 bg-warning-light rounded-lg">
                    <h3 className="font-semibold text-warning">Total Expenses</h3>
                    <p className="text-2xl font-bold text-warning">${getTotalExpenses()}</p>
                  </div>
                  <div className={`p-4 rounded-lg ${getNetBalance() >= 0 ? 'bg-success-light' : 'bg-destructive/10'}`}>
                    <h3 className={`font-semibold ${getNetBalance() >= 0 ? 'text-success' : 'text-destructive'}`}>
                      Net Balance
                    </h3>
                    <p className={`text-2xl font-bold ${getNetBalance() >= 0 ? 'text-success' : 'text-destructive'}`}>
                      ${getNetBalance()}
                    </p>
                  </div>
                </div>
                
                <div className="flex gap-4">
                  <Button>Generate Yearly Report</Button>
                  <Button variant="outline">Export to PDF</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MaintenanceTracker;