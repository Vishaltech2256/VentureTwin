import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Building2,
  DollarSign,
  Users,
  MapPin,
  Compass,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  AlertCircle,
} from 'lucide-react';
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
import { formatINR } from '../utils/formatters';
import { normalizeError } from '../utils/errors';

export const CreateStartupPage: React.FC = () => {
  const navigate = useNavigate();
  const { refreshStartups, setActiveStartupId } = useApp();

  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);

  // Step 1: Startup Profile
  const [startupName, setStartupName] = useState('');
  const [description, setDescription] = useState('');
  const [businessType, setBusinessType] = useState('SaaS');
  const [targetMarket, setTargetMarket] = useState('B2B');
  const [website, setWebsite] = useState('');
  const [foundedYear, setFoundedYear] = useState<number | ''>(new Date().getFullYear());

  // Step 2: Financial Information
  const [initialInvestment, setInitialInvestment] = useState<number | ''>('');
  const [monthlyExpenses, setMonthlyExpenses] = useState<number | ''>('');
  const [monthlyRevenue, setMonthlyRevenue] = useState<number | ''>('');
  const [annualRevenue, setAnnualRevenue] = useState<number | ''>('');
  const [fundingRaised, setFundingRaised] = useState<number | ''>('');
  const [burnRate, setBurnRate] = useState<number | ''>('');

  // Step 3: Team Information
  const [founderName, setFounderName] = useState('');
  const [founderExperienceYears, setFounderExperienceYears] = useState<number | ''>('');
  const [founderEducation, setFounderEducation] = useState('');
  const [employeeCount, setEmployeeCount] = useState<number | ''>('');
  const [teamSkills, setTeamSkills] = useState('');
  const [hasTechnicalCofounder, setHasTechnicalCofounder] = useState(false);

  // Step 4: Business Location
  const [country, setCountry] = useState('India');
  const [state, setState] = useState('');
  const [city, setCity] = useState('');
  const [address, setAddress] = useState('');
  const [pincode, setPincode] = useState('');

  // Step 5: Land Details
  const [hasLand, setHasLand] = useState(false);
  const [landStatus, setLandStatus] = useState<'owned' | 'rented' | 'no_land' | 'planning'>('rented');
  const [landAreaSqft, setLandAreaSqft] = useState<number | ''>('');
  const [landValue, setLandValue] = useState<number | ''>('');
  const [monthlyRent, setMonthlyRent] = useState<number | ''>('');
  const [expansionAvailable, setExpansionAvailable] = useState(false);

  // Validation errors
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});

  const validateStep = (step: number): boolean => {
    const errors: Record<string, string> = {};

    if (step === 1) {
      if (!startupName.trim()) {
        errors.startupName = 'Startup name is required.';
      } else if (startupName.length > 200) {
        errors.startupName = 'Startup name cannot exceed 200 characters.';
      }
      if (foundedYear !== '') {
        const yr = Number(foundedYear);
        if (yr < 1900 || yr > 2100) {
          errors.foundedYear = 'Founded year must be between 1900 and 2100.';
        }
      }
    }

    if (step === 2) {
      if (initialInvestment !== '' && Number(initialInvestment) < 0) {
        errors.initialInvestment = 'Must be greater than or equal to 0.';
      }
      if (monthlyExpenses !== '' && Number(monthlyExpenses) < 0) {
        errors.monthlyExpenses = 'Must be greater than or equal to 0.';
      }
      if (monthlyRevenue !== '' && Number(monthlyRevenue) < 0) {
        errors.monthlyRevenue = 'Must be greater than or equal to 0.';
      }
    }

    if (step === 3) {
      if (employeeCount !== '' && Number(employeeCount) < 0) {
        errors.employeeCount = 'Cannot be negative.';
      }
      if (founderExperienceYears !== '' && Number(founderExperienceYears) < 0) {
        errors.founderExperienceYears = 'Cannot be negative.';
      }
    }

    if (step === 5 && hasLand) {
      if (landAreaSqft !== '' && Number(landAreaSqft) < 0) {
        errors.landAreaSqft = 'Cannot be negative.';
      }
      if (landValue !== '' && Number(landValue) < 0) {
        errors.landValue = 'Cannot be negative.';
      }
      if (monthlyRent !== '' && Number(monthlyRent) < 0) {
        errors.monthlyRent = 'Cannot be negative.';
      }
    }

    setStepErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 6));
    }
  };

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  const handleSubmitAll = async () => {
    setGeneralError(null);
    setIsSubmitting(true);

    try {
      // 1. Create Core Startup Profile
      const newStartup = await startupApi.create({
        startup_name: startupName.trim(),
        description: description.trim() || null,
        business_type: businessType || null,
        target_market: targetMarket || null,
        website: website.trim() || null,
        founded_year: foundedYear !== '' ? Number(foundedYear) : null,
      });

      const startupId = newStartup.startup_id;

      // 2. Upsert Financial Information
      await financialApi.upsert(startupId, {
        initial_investment: initialInvestment !== '' ? Number(initialInvestment) : null,
        monthly_expenses: monthlyExpenses !== '' ? Number(monthlyExpenses) : null,
        monthly_revenue: monthlyRevenue !== '' ? Number(monthlyRevenue) : null,
        annual_revenue: annualRevenue !== '' ? Number(annualRevenue) : null,
        funding_raised: fundingRaised !== '' ? Number(fundingRaised) : null,
        burn_rate: burnRate !== '' ? Number(burnRate) : null,
      });

      // 3. Upsert Team Information
      await teamApi.upsert(startupId, {
        founder_name: founderName.trim() || null,
        founder_experience_years: founderExperienceYears !== '' ? Number(founderExperienceYears) : null,
        founder_education: founderEducation.trim() || null,
        employee_count: employeeCount !== '' ? Number(employeeCount) : null,
        team_skills: teamSkills.trim() || null,
        has_technical_cofounder: hasTechnicalCofounder,
      });

      // 4. Upsert Business Location
      await locationApi.upsert(startupId, {
        country: country.trim() || null,
        state: state.trim() || null,
        city: city.trim() || null,
        address: address.trim() || null,
        pincode: pincode.trim() || null,
      });

      // 5. Upsert Land Details
      await landApi.upsert(startupId, {
        has_land: hasLand,
        land_status: hasLand ? landStatus : 'no_land',
        land_area_sqft: hasLand && landAreaSqft !== '' ? Number(landAreaSqft) : null,
        land_value: hasLand && landValue !== '' ? Number(landValue) : null,
        monthly_rent: hasLand && monthlyRent !== '' ? Number(monthlyRent) : null,
        expansion_available: hasLand ? expansionAvailable : false,
      });

      // Refresh global state and navigate to newly created startup details
      await refreshStartups();
      setActiveStartupId(startupId);
      navigate(`/startups/${startupId}`);
    } catch (err) {
      const norm = normalizeError(err);
      setGeneralError(norm.message);
      if (Object.keys(norm.fieldErrors).length > 0) {
        setStepErrors(norm.fieldErrors);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const steps = [
    { num: 1, label: 'Profile', icon: <Building2 size={16} /> },
    { num: 2, label: 'Financials', icon: <DollarSign size={16} /> },
    { num: 3, label: 'Team', icon: <Users size={16} /> },
    { num: 4, label: 'Location', icon: <MapPin size={16} /> },
    { num: 5, label: 'Land', icon: <Compass size={16} /> },
    { num: 6, label: 'Review', icon: <CheckCircle2 size={16} /> },
  ];

  return (
    <div style={{ maxWidth: '840px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800 }}>Create Startup Profile</h1>
        <p style={{ marginTop: '0.25rem' }}>
          Complete the telemetry parameters to construct your digital twin simulation baseline.
        </p>
      </div>

      {/* Stepper Progress Navigation */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '1rem',
          backgroundColor: '#FFFFFF',
          border: '1px solid var(--color-border)',
          borderRadius: 'var(--radius-md)',
          overflowX: 'auto',
          gap: '0.5rem',
        }}
      >
        {steps.map((s, idx) => {
          const isActive = currentStep === s.num;
          const isDone = currentStep > s.num;
          return (
            <React.Fragment key={s.num}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  cursor: isDone ? 'pointer' : 'default',
                  opacity: isActive || isDone ? 1 : 0.45,
                }}
                onClick={() => isDone && setCurrentStep(s.num)}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    backgroundColor: isActive ? '#111111' : isDone ? '#444444' : '#F5F5F5',
                    color: isActive || isDone ? '#FFFFFF' : '#111111',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                  }}
                >
                  {isDone ? '✓' : s.num}
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: isActive ? 700 : 500, whiteSpace: 'nowrap' }}>
                  {s.label}
                </span>
              </div>
              {idx < steps.length - 1 && (
                <div style={{ flex: 1, minWidth: '15px', height: '1px', backgroundColor: '#E5E5E5' }} />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {generalError && (
        <div className="alert alert-danger" role="alert">
          <AlertCircle size={18} style={{ flexShrink: 0, marginTop: 2 }} />
          <div>{generalError}</div>
        </div>
      )}

      {/* Wizard Form Card */}
      <Card>
        {/* STEP 1: Startup Profile */}
        {currentStep === 1 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 1: General Profile</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Core identifying details for your enterprise entity.
            </p>

            <Input
              label="Startup Name"
              placeholder="e.g. Apex Dynamics AI"
              value={startupName}
              onChange={(e) => setStartupName(e.target.value)}
              error={stepErrors.startupName}
              required
            />

            <div className="form-group">
              <label className="form-label" htmlFor="business-type">
                <span>Business Type / Industry</span>
              </label>
              <select
                id="business-type"
                className="form-select"
                value={businessType}
                onChange={(e) => setBusinessType(e.target.value)}
              >
                <option value="SaaS">SaaS (Software as a Service)</option>
                <option value="Fintech">Fintech</option>
                <option value="E-commerce">E-commerce / Retail</option>
                <option value="AI/ML">Artificial Intelligence / ML</option>
                <option value="Healthtech">Healthtech / Biotech</option>
                <option value="Edtech">Edtech</option>
                <option value="Cleantech">Cleantech / Renewable</option>
                <option value="Manufacturing">Manufacturing & Hardware</option>
                <option value="Logistics">Supply Chain & Logistics</option>
                <option value="Services">Consulting & Professional Services</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="target-market">
                <span>Target Market</span>
              </label>
              <select
                id="target-market"
                className="form-select"
                value={targetMarket}
                onChange={(e) => setTargetMarket(e.target.value)}
              >
                <option value="B2B">B2B (Business to Business)</option>
                <option value="B2C">B2C (Business to Consumer)</option>
                <option value="B2B2C">B2B2C</option>
                <option value="Enterprise">Enterprise</option>
                <option value="D2C">D2C (Direct to Consumer)</option>
                <option value="Government">B2G / Public Sector</option>
              </select>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                label="Website URL"
                placeholder="https://example.com"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                optional
              />
              <Input
                label="Founded Year"
                type="number"
                placeholder="e.g. 2024"
                value={foundedYear}
                onChange={(e) => setFoundedYear(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.foundedYear}
                optional
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="description">
                <span>Business Description</span>
                <span className="form-label-optional">Optional</span>
              </label>
              <textarea
                id="description"
                rows={4}
                className="form-textarea"
                placeholder="Explain your core value proposition, problem addressed, and business model..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* STEP 2: Financial Information */}
        {currentStep === 2 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 2: Financial Telemetry</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Financial variables used by the prediction scoring engine. Values represented in INR (₹).
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                label="Initial Capital / Investment (₹)"
                type="number"
                placeholder="e.g. 500000"
                value={initialInvestment}
                onChange={(e) => setInitialInvestment(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.initialInvestment}
                helperText="Capital invested at inception"
                optional
              />

              <Input
                label="External Funding Raised (₹)"
                type="number"
                placeholder="e.g. 1000000"
                value={fundingRaised}
                onChange={(e) => setFundingRaised(e.target.value ? Number(e.target.value) : '')}
                helperText="Grants, angel or VC capital"
                optional
              />

              <Input
                label="Monthly Expenses (₹)"
                type="number"
                placeholder="e.g. 75000"
                value={monthlyExpenses}
                onChange={(e) => setMonthlyExpenses(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.monthlyExpenses}
                helperText="Payroll, cloud, rent, operations"
                optional
              />

              <Input
                label="Monthly Revenue (₹)"
                type="number"
                placeholder="e.g. 100000"
                value={monthlyRevenue}
                onChange={(e) => setMonthlyRevenue(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.monthlyRevenue}
                helperText="Current average monthly sales"
                optional
              />

              <Input
                label="Annual Revenue (₹)"
                type="number"
                placeholder="e.g. 1200000"
                value={annualRevenue}
                onChange={(e) => setAnnualRevenue(e.target.value ? Number(e.target.value) : '')}
                optional
              />

              <Input
                label="Estimated Monthly Burn Rate (₹)"
                type="number"
                placeholder="e.g. 25000"
                value={burnRate}
                onChange={(e) => setBurnRate(e.target.value ? Number(e.target.value) : '')}
                optional
              />
            </div>
          </div>
        )}

        {/* STEP 3: Team Information */}
        {currentStep === 3 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 3: Team Composition</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Human capital parameters contributing to operational capability scoring.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                label="Founder Full Name"
                placeholder="e.g. Priya Sharma"
                value={founderName}
                onChange={(e) => setFounderName(e.target.value)}
                optional
              />

              <Input
                label="Founder Experience (Years)"
                type="number"
                placeholder="e.g. 7"
                value={founderExperienceYears}
                onChange={(e) => setFounderExperienceYears(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.founderExperienceYears}
                optional
              />

              <Input
                label="Founder Education / Background"
                placeholder="e.g. B.Tech Computer Science, MBA"
                value={founderEducation}
                onChange={(e) => setFounderEducation(e.target.value)}
                optional
              />

              <Input
                label="Current Employee Count"
                type="number"
                placeholder="e.g. 5"
                value={employeeCount}
                onChange={(e) => setEmployeeCount(e.target.value ? Number(e.target.value) : '')}
                error={stepErrors.employeeCount}
                optional
              />
            </div>

            <div className="form-group" style={{ marginTop: '0.5rem' }}>
              <Input
                label="Core Team Skills (comma-separated)"
                placeholder="e.g. Python, React, Cloud Architecture, Marketing, Sales"
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
                padding: '1rem',
                backgroundColor: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                marginTop: '1rem',
              }}
            >
              <input
                id="technical-cofounder"
                type="checkbox"
                checked={hasTechnicalCofounder}
                onChange={(e) => setHasTechnicalCofounder(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#111111' }}
              />
              <label htmlFor="technical-cofounder" style={{ fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer' }}>
                Technical Co-founder Present (Provides an engineering score advantage)
              </label>
            </div>
          </div>
        )}

        {/* STEP 4: Business Location */}
        {currentStep === 4 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 4: Business Location</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Geographical operational base and registration address.
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <Input
                label="Country"
                placeholder="India"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                optional
              />

              <Input
                label="State / Province"
                placeholder="e.g. Karnataka, Maharashtra"
                value={state}
                onChange={(e) => setState(e.target.value)}
                optional
              />

              <Input
                label="City"
                placeholder="e.g. Bengaluru, Mumbai, Pune"
                value={city}
                onChange={(e) => setCity(e.target.value)}
                optional
              />

              <Input
                label="Postal Pincode"
                placeholder="e.g. 560001"
                value={pincode}
                onChange={(e) => setPincode(e.target.value)}
                optional
              />
            </div>

            <div className="form-group" style={{ marginTop: '0.5rem' }}>
              <label className="form-label" htmlFor="address">
                <span>Registered Business Address</span>
                <span className="form-label-optional">Optional</span>
              </label>
              <textarea
                id="address"
                rows={3}
                className="form-textarea"
                placeholder="Street address, building, suite..."
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>
          </div>
        )}

        {/* STEP 5: Land Details (Conditional) */}
        {currentStep === 5 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 5: Physical Land & Premises</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Physical real estate occupancy details for physical/manufacturing facilities.
            </p>

            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
                padding: '1rem',
                backgroundColor: 'var(--color-bg-secondary)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '1.5rem',
              }}
            >
              <input
                id="has-land-check"
                type="checkbox"
                checked={hasLand}
                onChange={(e) => setHasLand(e.target.checked)}
                style={{ width: '18px', height: '18px', accentColor: '#111111' }}
              />
              <label htmlFor="has-land-check" style={{ fontSize: '0.875rem', fontWeight: 600, cursor: 'pointer' }}>
                Does this venture utilize dedicated physical land or commercial premises?
              </label>
            </div>

            {hasLand ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }} className="animate-fade-in">
                <div className="form-group">
                  <label className="form-label" htmlFor="land-status">
                    <span>Premises Status</span>
                  </label>
                  <select
                    id="land-status"
                    className="form-select"
                    value={landStatus}
                    onChange={(e) => setLandStatus(e.target.value as any)}
                  >
                    <option value="rented">Rented / Leased</option>
                    <option value="owned">Owned</option>
                    <option value="planning">In Planning / Acquisition</option>
                  </select>
                </div>

                <Input
                  label="Area (Square Feet)"
                  type="number"
                  placeholder="e.g. 2400"
                  value={landAreaSqft}
                  onChange={(e) => setLandAreaSqft(e.target.value ? Number(e.target.value) : '')}
                  error={stepErrors.landAreaSqft}
                  optional
                />

                <Input
                  label="Estimated Land Value (₹)"
                  type="number"
                  placeholder="e.g. 5000000"
                  value={landValue}
                  onChange={(e) => setLandValue(e.target.value ? Number(e.target.value) : '')}
                  error={stepErrors.landValue}
                  optional
                />

                <Input
                  label="Monthly Rent (₹)"
                  type="number"
                  placeholder="e.g. 45000"
                  value={monthlyRent}
                  onChange={(e) => setMonthlyRent(e.target.value ? Number(e.target.value) : '')}
                  error={stepErrors.monthlyRent}
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
                    id="expansion-check"
                    type="checkbox"
                    checked={expansionAvailable}
                    onChange={(e) => setExpansionAvailable(e.target.checked)}
                    style={{ width: '18px', height: '18px', accentColor: '#111111' }}
                  />
                  <label htmlFor="expansion-check" style={{ fontSize: '0.85rem', fontWeight: 600, cursor: 'pointer' }}>
                    Physical expansion space available at premises
                  </label>
                </div>
              </div>
            ) : (
              <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
                No land claimed. Suitable for digital, remote, and software ventures.
              </p>
            )}
          </div>
        )}

        {/* STEP 6: Review & Submit */}
        {currentStep === 6 && (
          <div className="animate-fade-in">
            <h3 style={{ fontSize: '1.25rem', marginBottom: '0.25rem' }}>Step 6: Review Parameters</h3>
            <p style={{ fontSize: '0.85rem', marginBottom: '1.5rem' }}>
              Verify all entered information before registering the startup profile with the backend.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Profile Review */}
              <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem' }}>1. Startup Profile</h4>
                  <button className="btn btn-secondary btn-sm" onClick={() => setCurrentStep(1)}>Edit</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div><strong>Name:</strong> {startupName || '—'}</div>
                  <div><strong>Industry:</strong> {businessType}</div>
                  <div><strong>Target:</strong> {targetMarket}</div>
                  <div><strong>Founded:</strong> {foundedYear || '—'}</div>
                  {website && <div style={{ gridColumn: 'span 2' }}><strong>Website:</strong> {website}</div>}
                  {description && <div style={{ gridColumn: 'span 2' }}><strong>Description:</strong> {description}</div>}
                </div>
              </div>

              {/* Financial Review */}
              <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem' }}>2. Financials</h4>
                  <button className="btn btn-secondary btn-sm" onClick={() => setCurrentStep(2)}>Edit</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div><strong>Initial Capital:</strong> {formatINR(initialInvestment !== '' ? Number(initialInvestment) : null)}</div>
                  <div><strong>Funding Raised:</strong> {formatINR(fundingRaised !== '' ? Number(fundingRaised) : null)}</div>
                  <div><strong>Monthly Revenue:</strong> {formatINR(monthlyRevenue !== '' ? Number(monthlyRevenue) : null)}</div>
                  <div><strong>Monthly Expenses:</strong> {formatINR(monthlyExpenses !== '' ? Number(monthlyExpenses) : null)}</div>
                </div>
              </div>

              {/* Team Review */}
              <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem' }}>3. Team</h4>
                  <button className="btn btn-secondary btn-sm" onClick={() => setCurrentStep(3)}>Edit</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div><strong>Founder:</strong> {founderName || '—'} ({founderExperienceYears ? `${founderExperienceYears} yrs` : '—'})</div>
                  <div><strong>Team Size:</strong> {employeeCount !== '' ? `${employeeCount} members` : '—'}</div>
                  <div><strong>Tech Co-founder:</strong> {hasTechnicalCofounder ? 'Yes' : 'No'}</div>
                  <div><strong>Skills:</strong> {teamSkills || '—'}</div>
                </div>
              </div>

              {/* Location & Land Review */}
              <div style={{ border: '1px solid var(--color-border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '0.95rem' }}>4. Location & Premises</h4>
                  <button className="btn btn-secondary btn-sm" onClick={() => setCurrentStep(4)}>Edit</button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.85rem' }}>
                  <div><strong>Location:</strong> {[city, state, country].filter(Boolean).join(', ') || '—'}</div>
                  <div><strong>Physical Land:</strong> {hasLand ? `${landStatus} (${landAreaSqft || 0} sqft)` : 'No physical premises'}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Wizard Control Buttons */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginTop: '2rem',
            paddingTop: '1.25rem',
            borderTop: '1px solid var(--color-border)',
          }}
        >
          <div>
            {currentStep > 1 && (
              <Button
                variant="secondary"
                onClick={prevStep}
                disabled={isSubmitting}
                leftIcon={<ArrowLeft size={16} />}
              >
                Previous Step
              </Button>
            )}
          </div>

          <div>
            {currentStep < 6 ? (
              <Button
                variant="primary"
                onClick={nextStep}
                rightIcon={<ArrowRight size={16} />}
              >
                Next Step
              </Button>
            ) : (
              <Button
                variant="primary"
                onClick={handleSubmitAll}
                isLoading={isSubmitting}
                rightIcon={<CheckCircle2 size={16} />}
              >
                Register Startup Profile
              </Button>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
};
