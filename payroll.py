import React, { useState } from 'react';
import { createClient } from '@supabase/supabase-js';

// Initialize Supabase Client (Replace with your project credentials)
const supabaseUrl = 'YOUR_SUPABASE_URL';
const supabaseKey = 'YOUR_SUPABASE_ANON_KEY';
const supabase = createClient(supabaseUrl, supabaseKey);

export default function MiragePayrollApp() {
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Handle Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Query employee by ID (الرقم القومي)
      const { data, error } = await supabase
        .from('employees')
        .select('*')
        .eq('employee_id', employeeId)
        .single();

      if (error || !data) {
        throw new Error('Invalid Employee ID or password.');
      }

      // In production, verify hashed password. Here we match plain or hashed password check:
      if (data.password_hash !== password) {
        throw new Error('Invalid Employee ID or password.');
      }

      setUser(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle Logout
  const handleLogout = () => {
    setUser(null);
    setEmployeeId('');
    setPassword('');
  };

  // If not logged in, show Login Screen
  if (!user) {
    return (
      <div style={styles.container}>
        <div style={styles.card}>
          <h2 style={styles.title}>Mirage Employee Portal</h2>
          <p style={styles.subtitle}>Sign in with your ID and custom password</p>
          
          {error && <div style={styles.error}>{error}</div>}

          <form onSubmit={handleLogin} style={styles.form}>
            <div style={styles.inputGroup}>
              <label style={styles.label}>Employee ID (الرقم القومي)</label>
              <input
                type="text"
                value={employeeId}
                onChange={(e) => setEmployeeId(e.target.value)}
                placeholder="Enter your ID..."
                required
                style={styles.input}
              />
            </div>

            <div style={styles.inputGroup}>
              <label style={styles.label}>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password..."
                required
                style={styles.input}
              />
            </div>

            <button type="submit" disabled={loading} style={styles.button}>
              {loading ? 'Signing in...' : 'Login'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Calculate Final Salary
  const baseSalary = Number(user.base_salary) || 0;
  const bonuses = Number(user.bonuses) || 0;
  const salaryCuts = Number(user.salary_cuts) || 0;
  const finalSalary = baseSalary + bonuses - salaryCuts;

  // If logged in, show Employee Dashboard / Payslip
  return (
    <div style={styles.container}>
      <div style={styles.dashboardCard}>
        <div style={styles.headerRow}>
          <div>
            <h2 style={styles.welcomeText}>Welcome, {user.full_name}</h2>
            <p style={styles.subText}>Employee ID: {user.employee_id}</p>
          </div>
          <button onClick={handleLogout} style={styles.logoutButton}>Logout</button>
        </div>

        <hr style={styles.divider} />

        <h3 style={styles.sectionTitle}>Monthly Salary & Attendance Breakdown</h3>

        <div style={styles.grid}>
          <div style={styles.metricCard}>
            <span style={styles.metricLabel}>Main Salary (الراتب الاساسي)</span>
            <span style={styles.metricValue}>${baseSalary.toLocaleString()}</span>
          </div>
          <div style={styles.metricCard}>
            <span style={styles.metricLabel}>Days Off (ايام الراحة/الغياب)</span>
            <span style={styles.metricValue}>{user.days_off || 0} Days</span>
          </div>
          <div style={styles.metricCard}>
            <span style={styles.metricLabel}>Days Late (ايام التأخير)</span>
            <span style={styles.metricValue}>{user.days_late || 0} Days</span>
          </div>
          <div style={styles.metricCard}>
            <span style={styles.metricLabel}>Bonuses (المكافآت)</span>
            <span style={{ ...styles.metricValue, color: '#10B981' }}>+${bonuses.toLocaleString()}</span>
          </div>
          <div style={styles.metricCard}>
            <span style={styles.metricLabel}>Salary Cuts (الخصومات)</span>
            <span style={{ ...styles.metricValue, color: '#EF4444' }}>-${salaryCuts.toLocaleString()}</span>
          </div>
        </div>

        <div style={styles.totalBox}>
          <span style={styles.totalLabel}>Final Net Salary (صافي الراتب النهائي)</span>
          <span style={styles.totalValue}>${finalSalary.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

// Clean professional inline styles
const styles = {
  container: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', backgroundColor: '#F3F4F6', fontFamily: 'Segoe UI, sans-serif', padding: '20px' },
  card: { backgroundColor: '#FFFFFF', padding: '40px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '100%', maxWidth: '400px' },
  dashboardCard: { backgroundColor: '#FFFFFF', padding: '30px', borderRadius: '12px', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', width: '100%', maxWidth: '700px' },
  title: { fontSize: '24px', fontWeight: 'bold', color: '#1F2937', marginBottom: '8px', textAlign: 'center' },
  subtitle: { fontSize: '14px', color: '#6B7280', marginBottom: '24px', textAlign: 'center' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '6px' },
  label: { fontSize: '14px', fontWeight: '600', color: '#374151' },
  input: { padding: '10px 14px', borderRadius: '8px', border: '1px solid #D1D5DB', fontSize: '16px', outline: 'none' },
  button: { backgroundColor: '#2563EB', color: '#FFFFFF', padding: '12px', borderRadius: '8px', border: 'none', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px' },
  error: { backgroundColor: '#FEE2E2', color: '#B91C1C', padding: '10px', borderRadius: '6px', fontSize: '14px', marginBottom: '16px', textAlign: 'center' },
  headerRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  welcomeText: { fontSize: '20px', fontWeight: 'bold', color: '#1F2937' },
  subText: { fontSize: '13px', color: '#6B7280', marginTop: '2px' },
  logoutButton: { backgroundColor: '#EF4444', color: '#FFF', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' },
  divider: { border: '0', height: '1px', backgroundColor: '#E5E7EB', margin: '20px 0' },
  sectionTitle: { fontSize: '16px', fontWeight: '600', color: '#374151', marginBottom: '16px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '24px' },
  metricCard: { backgroundColor: '#F9FAFB', padding: '16px', borderRadius: '8px', border: '1px solid #E5E7EB', display: 'flex', flexDirection: 'column', gap: '6px' },
  metricLabel: { fontSize: '12px', color: '#6B7280', fontWeight: '500' },
  metricValue: { fontSize: '18px', fontWeight: 'bold', color: '#1F2937' },
  totalBox: { backgroundColor: '#EFF6FF', border: '1px solid #BFDBFE', padding: '20px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  totalLabel: { fontSize: '16px', fontWeight: 'bold', color: '#1E40AF' },
  totalValue: { fontSize: '24px', fontWeight: 'bold', color: '#1E40AF' }
};
