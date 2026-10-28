import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Save, AlertCircle, CheckCircle2 } from 'lucide-react';
import {
  startupApi,
  financialApi,
  teamApi,
  locationApi,
  landApi,
} from '../api/startups';
import { useApp } from '../components/layout/AppLayout';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { LoadingState } from '../components/feedback/LoadingState';
import { ErrorState } from '../components/feedback/ErrorState';
import { normalizeError } from '../utils/errors';

export const EditStartupPage: React.FC = () => {
  const { startupId } = useParams<{ startupId: string }>();
  const navigate = useNavigate();
  const { refreshStartups } = useApp();

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Section 1: Profile
  const [startupName, setStartupName] = useState('');
  const [description, setDescription] = useState('');
  const [businessType, setBusinessType] = useState('SaaS');
  const [targetMarket, setTargetMarket] = useState('B2B');
  const [website, setWebsite] = useState('');
  const [foundedYear, setFoundedYear] = useState<number | ''>('');

  // Section 2: Financials
  const [initialInvestment, setInitialInvestment] = useState<number | ''>('');
  const [monthlyExpenses, setMonthlyExpenses] = useState<number | ''>('');
  const [monthlyRevenue, setMonthlyRevenue] = useState<number | ''>('');
  const [annualRevenue, setAnnualRevenue] = useState<number | ''>('');
  const [fundingRaised, setFundingRaised] = useState<number | ''>('');
  const [burnRate, setBurnRate] = useState<number | ''>('');

  // Section 3: Team
  const [founderName, setFounderName] = useState('');
  const [founderExperienceYears, setFounderExperienceYears] = useState<number | ''>('');
  const [founderEducation, setFounderEducation] = useState('');
  const [employeeCount, setEmployeeCount] = useState<number | ''>('');
  const [teamSkills, setTeamSkills] = useState('');
  const [hasTechnicalCofounder, setHasTechnicalCofounder] = useState(false);

  // Section 4: Location
  const [country, setCountry] = useState('');
  const [state, setState] = useState('');
  const [city, setCity] = useState('');
  const [address, setAddress] = useState('');
  const [pincode, setPincode] = useState('');

  // Section 5: Land
  const [hasLand, setHasLand] = useState(false);
  const [landStatus, setLandStatus] = useState<string>('rented');
  const [landAreaSqft, setLandAreaSqft] = useState<number | ''>('');
  const [landValue, setLandValue] = useState<number | ''>('');
  const [monthlyRent, setMonthlyRent] = useState<number | ''>('');
  const [expansionAvailable, setExpansionAvailable] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});

  const loadData = useCallback(async () => {
    if (!startupId) return;
    setIsLoading(true);
    setLoadError(null);
    try {
      const full = await startupApi.getFull(Number(startupId));

      // Populate profile
      setStartupName(full.profile.startup_name || '');
      setDescription(full.profile.description || '');
      setBusinessType(full.profile.business_type || 'SaaS');
      setTargetMarket(full.profile.target_market || 'B2B');
      setWebsite(full.profile.website || '');
      setFoundedYear(full.profile.founded_year || '');

      // Populate financial
      if (full.financial) {
        setInitialInvestment(full.financial.initial_investment ?? '');
        setMonthlyExpenses(full.financial.monthly_expenses ?? '');
        setMonthlyRevenue(full.financial.monthly_revenue ?? '');
        setAnnualRevenue(full.financial.annual_revenue ?? '');
        setFundingRaised(full.financial.funding_raised ?? '');
        setBurnRate(full.financial.burn_rate ?? '');
      }

      // Populate team
      if (full.team) {
        setFounderName(full.team.founder_name || '');
        setFounderExperienceYears(full.team.founder_experience_years ?? '');
        setFounderEducation(full.team.founder_education || '');
        setEmployeeCount(full.team.employee_count ?? '');
        setTeamSkills(full.team.team_skills || '');
        setHasTechnicalCofounder(full.team.has_technical_cofounder);
      }

      // Populate location
      if (full.location) {
        setCountry(full.location.country || '');
        setState(full.location.state || '');
        setCity(full.location.city || '');
        setAddress(full.location.address || '');
        setPincode(full.location.pincode || '');
      }

      // Populate land
      if (full.land) {
        setHasLand(full.land.has_land);
        setLandStatus(full.land.land_status || 'rented');
        setLandAreaSqft(full.land.land_area_sqft ?? '');
        setLandValue(full.land.land_value ?? '');
        setMonthlyRent(full.land.monthly_rent ?? '');
        setExpansionAvailable(full.land.expansion_available);
      }
    } catch (err) {
      const norm = normalizeError(err);
      setLoadError(norm.message);
    } finally {
      setIsLoading(false);
    }
  }, [startupId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!startupId) return;

    setSaveError(null);
    setSaveSuccess(false);

    if (!startupName.trim()) {
      setErrors({ startupName: 'Startup name cannot be blank.' });
      return;
    }

    setIsSaving(true);
    const id = Number(startupId);

    try {
      // 1. Update Profile via PATCH /startup-profile/{id}
      await startupApi.update(id, {
        startup_name: startupName.trim(),
        description: description.trim() || null,
        business_type: businessType || null,
        target_market: targetMarket || null,
        website: website.trim() || null,
        founded_year: foundedYear !== '' ? Number(foundedYear) : null,
      });

      // 2. Upsert Financials
      await financialApi.upsert(id, {
        initial_investment: initialInvestment !== '' ? Number(initialInvestment) : null,
        monthly_expenses: monthlyExpenses !== '' ? Number(monthlyExpenses) : null,
        monthly_revenue: monthlyRevenue !== '' ? Number(monthlyRevenue) : null,
        annual_revenue: annualRevenue !== '' ? Number(annualRevenue) : null,
        funding_raised: fundingRaised !== '' ? Number(fundingRaised) : null,
        burn_rate: burnRate !== '' ? Number(burnRate) : null,
      });

      // 3. Upsert Team
      await teamApi.upsert(id, {
        founder_name: founderName.trim() || null,
        founder_experience_years: founderExperienceYears !== '' ? Number(founderExperienceYears) : null,
        founder_education: founderEducation.trim() || null,
        employee_count: employeeCount !== '' ? Number(employeeCount) : null,
        team_skills: teamSkills.trim() || null,
        has_technical_cofounder: hasTechnicalCofounder,
      });

      // 4. Upsert Location
      await locationApi.upsert(id, {
        country: country.trim() || null,
        state: state.trim() || null,
        city: city.trim() || null,
        address: address.trim() || null,
        pincode: pincode.trim() || null,
      });

      // 5. Upsert Land
      await landApi.upsert(id, {
        has_land: hasLand,
        land_status: hasLand ? landStatus : 'no_land',
        land_area_sqft: hasLand && landAreaSqft !== '' ? Number(landAreaSqft) : null,
        land_value: hasLand && landValue !== '' ? Number(landValue) : null,
        monthly_rent: hasLand && monthlyRent !== '' ? Number(monthlyRent) : null,
        expansion_available: hasLand ? expansionAvailable : false,
      });

      await refreshStartups();
      setSaveSuccess(true);
      setTimeout(() => {
        navigate(`/startups/${id}`);
      }, 800);
    } catch (err) {
      const norm = normalizeError(err);
      setSaveError(norm.message);
      if (Object.keys(norm.fieldErrors).length > 0) {
        setErrors(norm.fieldErrors);
      }
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <LoadingState message="Loading current startup parameters..." />;
  }

  if (loadError) {
    return (
      <ErrorState
        title="Could not load startup"
        message={loadError}
        onRetry={loadData}
      />
    );
  }

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <Link
          to={`/startups/${startupId}`}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.4rem',
            fontSize: '0.85rem',
            color: 'var(--color-text-secondary)',
            fontWeight: 500,
            marginBottom: '0.75rem',
          }}
        >
          <ArrowLeft size={14} />
          <span>Back to Startup Details</span>
        </Link>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Edit Startup Profile</h1>
        <p style={{ marginTop: '0.25rem' }}>
          Update core business attributes, financial figures, team structure, and premises.
        </p>
      </div>

      {saveError && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>{saveError}</div>
        </div>
      )}

      {saveSuccess && (
        <div className="alert alert-success" role="alert">
          <CheckCircle2 size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>Startup telemetry updated successfully! Navigating to profile...</div>
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* Profile Card */}
        <Card title="1. Startup Profile">
          <Input
            label="Startup Name"
            value={startupName}
            onChange={(e) => setStartupName(e.target.value)}
            error={errors.startupName}
            required
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="edit-business-type">
                <span>Business Type / Industry</span>
              </label>
              <select
                id="edit-business-type"
                className="form-select"
                value={businessType}
                onChange={(e) => setBusinessType(e.target.value)}
              >
                <option value="SaaS">SaaS</option>
                <option value="Fintech">Fintech</option>
                <option value="E-commerce">E-commerce</option>
                <option value="AI/ML">AI / Machine Learning</option>
                <option value="Healthtech">Healthtech</option>
                <option value="Edtech">Edtech</option>
                <option value="Cleantech">Cleantech</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Logistics">Logistics</option>
                <option value="Services">Services</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="edit-target-market">
                <span>Target Market</span>
              </label>
              <select
                id="edit-target-market"
                className="form-select"
                value={targetMarket}
                onChange={(e) => setTargetMarket(e.target.value)}
              >
                <option value="B2B">B2B</option>
                <option value="B2C">B2C</option>
                <option value="B2B2C">B2B2C</option>
                <option value="Enterprise">Enterprise</option>
                <option value="D2C">D2C</option>
                <option value="Government">Government / B2G</option>
              </select>
            </div>

            <Input
              label="Website URL"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              optional
            />

            <Input
              label="Founded Year"
              type="number"
              value={foundedYear}
              onChange={(e) => setFoundedYear(e.target.value ? Number(e.target.value) : '')}
              optional
            />
          </div>

          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="form-label" htmlFor="edit-description">
              <span>Business Description</span>
              <span className="form-label-optional">Optional</span>
            </label>
            <textarea
              id="edit-description"
              rows={4}
              className="form-textarea"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
        </Card>

        {/* Financials Card */}
        <Card title="2. Financial Information">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Initial Capital / Investment (₹)"
              type="number"
              value={initialInvestment}
              onChange={(e) => setInitialInvestment(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="External Funding Raised (₹)"
              type="number"
              value={fundingRaised}
              onChange={(e) => setFundingRaised(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="Monthly Expenses (₹)"
              type="number"
              value={monthlyExpenses}
              onChange={(e) => setMonthlyExpenses(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="Monthly Revenue (₹)"
              type="number"
              value={monthlyRevenue}
              onChange={(e) => setMonthlyRevenue(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="Annual Revenue (₹)"
              type="number"
              value={annualRevenue}
              onChange={(e) => setAnnualRevenue(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="Burn Rate (₹)"
              type="number"
              value={burnRate}
              onChange={(e) => setBurnRate(e.target.value ? Number(e.target.value) : '')}
              optional
            />
          </div>
        </Card>

        {/* Team Card */}
        <Card title="3. Team Information">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Founder Full Name"
              value={founderName}
              onChange={(e) => setFounderName(e.target.value)}
              optional
            />
            <Input
              label="Founder Experience (Years)"
              type="number"
              value={founderExperienceYears}
              onChange={(e) => setFounderExperienceYears(e.target.value ? Number(e.target.value) : '')}
              optional
            />
            <Input
              label="Founder Education"
              value={founderEducation}
              onChange={(e) => setFounderEducation(e.target.value)}
              optional
            />
            <Input
              label="Employee Count"
              type="number"
              value={employeeCount}
              onChange={(e) => setEmployeeCount(e.target.value ? Number(e.target.value) : '')}
              optional
            />
          </div>

          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <Input
              label="Team Skills (comma-separated)"
              value={teamSkills}
              onChange={(e) => setTeamSkills(e.target.value)}
              optional
            />
          </div>

          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.85rem',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: 'var(--radius-sm)',
            }}
          >
            <input
              id="edit-tech-cofounder"
              type="checkbox"
              checked={hasTechnicalCofounder}
              onChange={(e) => setHasTechnicalCofounder(e.target.checked)}
              style={{ width: '18px', height: '18px', accentColor: '#111111' }}
            />
            <label htmlFor="edit-tech-cofounder" style={{ fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer' }}>
              Technical Co-founder Present
            </label>
          </div>
        </Card>

        {/* Location Card */}
        <Card title="4. Business Location">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              label="Country"
              value={country}
              onChange={(e) => setCountry(e.target.value)}
              optional
            />
            <Input
              label="State / Province"
              value={state}
              onChange={(e) => setState(e.target.value)}
              optional
            />
            <Input
              label="City"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              optional
            />
            <Input
              label="Postal Pincode"
              value={pincode}
              onChange={(e) => setPincode(e.target.value)}
              optional
            />
          </div>

          <div className="form-group" style={{ marginTop: '0.5rem' }}>
            <label className="form-label" htmlFor="edit-address">
              <span>Registered Business Address</span>
              <span className="form-label-optional">Optional</span>
            </label>
            <textarea
              id="edit-address"
              rows={3}
              className="form-textarea"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>
        </Card>

        {/* Land Card */}
        <Card title="5. Land Details">
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.85rem',
              backgroundColor: 'var(--color-bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '1rem',
            }}
          >
            <input
              id="edit-has-land"
              type="checkbox"
              checked={hasLand}
              onChange={(e) => setHasLand(e.target.checked)}
              style={{ width: '18px', height: '18px', accentColor: '#111111' }}
            />
            <label htmlFor="edit-has-land" style={{ fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer' }}>
              Venture utilizes dedicated physical commercial land or premises
            </label>
          </div>

          {hasLand && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label" htmlFor="edit-land-status">
                  <span>Premises Status</span>
                </label>
                <select
                  id="edit-land-status"
                  className="form-select"
                  value={landStatus}
                  onChange={(e) => setLandStatus(e.target.value)}
                >
                  <option value="rented">Rented / Leased</option>
                  <option value="owned">Owned</option>
                  <option value="planning">In Planning</option>
                </select>
              </div>

              <Input
                label="Area (Square Feet)"
                type="number"
                value={landAreaSqft}
                onChange={(e) => setLandAreaSqft(e.target.value ? Number(e.target.value) : '')}
                optional
              />

              <Input
                label="Estimated Land Value (₹)"
                type="number"
                value={landValue}
                onChange={(e) => setLandValue(e.target.value ? Number(e.target.value) : '')}
                optional
              />

              <Input
                label="Monthly Rent (₹)"
                type="number"
                value={monthlyRent}
                onChange={(e) => setMonthlyRent(e.target.value ? Number(e.target.value) : '')}
                optional
              />

              <div
                style={{
                  gridColumn: 'span 2',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '0.75rem',
                  backgroundColor: 'var(--color-bg-secondary)',
                  borderRadius: 'var(--radius-sm)',
                }}
              >
                <input
                  id="edit-expansion-check"
                  type="checkbox"
                  checked={expansionAvailable}
                  onChange={(e) => setExpansionAvailable(e.target.checked)}
                  style={{ width: '18px', height: '18px', accentColor: '#111111' }}
                />
                <label htmlFor="edit-expansion-check" style={{ fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>
                  Expansion space available at premises
                </label>
              </div>
            </div>
          )}
        </Card>

        {/* Action Bottom Bar */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid var(--color-border)',
          }}
        >
          <Link to={`/startups/${startupId}`}>
            <Button variant="secondary" disabled={isSaving}>
              Cancel
            </Button>
          </Link>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSaving}
            leftIcon={<Save size={16} />}
          >
            Save All Changes
          </Button>
        </div>
      </form>
    </div>
  );
};
