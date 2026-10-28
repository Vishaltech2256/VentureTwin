# VentureTwin Professional Frontend

Enterprise-grade, monochrome frontend for the **VentureTwin: Startup Digital Twin AI Platform**. Fully integrated with the FastAPI backend, adhering strictly to its registered endpoints, Pydantic data schemas, and SQLAlchemy data models.

---

## 1. Runtime & Package Specifications

- **Node.js**: `v20.x` or higher (verified with `v24.15.0`)
- **Package Manager**: `npm` `v10.x` or higher (verified with `v11.12.1`)
- **Core Framework**: React `19.0.0`
- **Language**: TypeScript `5.7.x`
- **Bundler & Dev Server**: Vite `6.2.x`
- **Routing**: React Router DOM `7.2.x`
- **HTTP Client**: Axios `1.7.9`
- **Iconography**: Lucide React `0.475.0` (monochrome)

---

## 2. Directory Structure

```
ven frontend/
├── dist/                      # Production build bundle
├── public/                    # Static public assets
├── src/
│   ├── api/                   # Typed API integration layer
│   │   ├── client.ts          # Axios client with Bearer auth & token refresh
│   │   ├── auth.ts            # Authentication (/auth/login, /auth/register, /auth/token, /auth/me)
│   │   ├── startups.ts        # Startup profile & subresource CRUD (financial, team, location, land)
│   │   ├── dashboard.ts       # Global telemetry dashboard (/dashboard/)
│   │   ├── predictions.ts     # Prediction simulation runs (/predictions/run/{id}, /latest)
│   │   ├── suggestions.ts     # AI recommendation generation & lifecycle (/ai-suggestions)
│   │   └── reports.ts         # Executive PDF report generation & authenticated download (/reports)
│   ├── components/
│   │   ├── feedback/          # LoadingState, ErrorState, EmptyState
│   │   ├── layout/            # AppLayout, Header, Sidebar
│   │   └── ui/                # Button, Input, Card, Badge, Modal
│   ├── context/
│   │   └── AuthContext.tsx    # Session state, JWT storage, and auth workflows
│   ├── pages/
│   │   ├── LandingPage.tsx        # Public welcome & overview ("Understand Your Startup Before You Scale")
│   │   ├── RegisterPage.tsx       # Account registration with schema validation
│   │   ├── LoginPage.tsx          # Form-encoded OAuth2 & JSON sign-in
│   │   ├── DashboardPage.tsx      # Platform overview, metrics, and active startup telemetry
│   │   ├── StartupsPage.tsx       # Registry grid, search filter, and delete modal
│   │   ├── CreateStartupPage.tsx  # 6-step wizard (Profile -> Financials -> Team -> Location -> Land -> Review)
│   │   ├── StartupDetailPage.tsx  # Complete tabbed telemetry inspector
│   │   ├── EditStartupPage.tsx    # Full profile and subresource editing
│   │   ├── PredictionsPage.tsx    # Rule-based prediction engine & history
│   │   ├── SuggestionsPage.tsx    # Contextual strategic advice & category filtering
│   │   ├── ReportsPage.tsx        # PDF generator & authenticated file downloader
│   │   └── AccountPage.tsx        # Founder account profile update & sign out
│   ├── styles/
│   │   ├── variables.css      # Monochrome design tokens (#FFFFFF, #111111, #F5F5F5, #E5E5E5)
│   │   └── index.css          # Global typography, layout, and component styling
│   ├── types/
│   │   └── index.ts           # Exact TypeScript representations of backend Pydantic models
│   ├── utils/
│   │   ├── errors.ts          # FastAPI / Pydantic error normalization
│   │   └── formatters.ts      # Indian Rupee (INR ₹), date, percentage, and assumption parsing
│   ├── App.tsx                # Centralized router configuration
│   ├── main.tsx               # Application bootstrap
│   └── vite-env.d.ts          # Vite client environment typing
├── .env                       # Local environment variables
├── .env.example               # Environment template
├── package.json
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

---

## 3. Environment Configuration

The frontend communicates with the FastAPI backend using `VITE_API_BASE_URL`.

Create or edit `.env` in the root folder:

```env
# Verified FastAPI active router prefix is /api/v1
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

*(Never place database passwords, JWT signing keys, or server secrets in frontend code or frontend `.env` files.)*

---

## 4. Backend Prerequisites & Startup

Before launching the frontend, ensure the backend dependencies and database are initialized.

### A. Database Prerequisites
The backend connects to PostgreSQL via `DATABASE_URL`. Ensure PostgreSQL is active on port `5432` with the database `VentureTwin` created:

```bash
# Verify PostgreSQL is running
# Default backend URL in backend/.env:
DATABASE_URL=postgresql+psycopg2://postgres:<password>@localhost:5432/VentureTwin
```

### B. Backend Startup Command
From the backend directory:

```bash
cd "C:\Users\visha\Documents\venture twin original\VentureTwin-main\backend"

# Activate the existing virtual environment:
.venv\Scripts\activate

# Run Uvicorn server:
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### C. Verify Backend Health & API Docs
- **Health Check**: Visit `http://127.0.0.1:8000/api/v1/health` in your browser. Expected response:
  ```json
  {"status": "ok", "app": "VentureTwin", "version": "1.0.0"}
  ```
- **Swagger Interactive API Documentation**: Open `http://127.0.0.1:8000/docs` to inspect active schemas and test endpoints.

---

## 5. Frontend Startup & Production Build

### A. Dependency Installation
```bash
cd "c:\Users\visha\ven frontend"
npm install
```

### B. Run Development Server
```bash
npm run dev
```
The application will launch at `http://localhost:5173`.

### C. Build for Production
```bash
npm run build
```
This runs TypeScript validation (`tsc`) followed by Vite's production bundling (`vite build`) outputting into `dist/`.

### D. Preview Production Build
```bash
npm run preview
```

---

## 6. Backend Endpoint to Frontend Page Mapping

| Feature | Backend Endpoint | Method | Frontend Page | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Health** | `/api/v1/health` | `GET` | All | Backend liveness verification |
| **Register** | `/api/v1/auth/register` | `POST` | `/register` | Create account (`UserRegisterRequest`) |
| **Login (Form)** | `/api/v1/auth/token` | `POST` | `/login` | OAuth2 form authentication (`username`, `password`) |
| **Login (JSON)** | `/api/v1/auth/login` | `POST` | `/login` | Direct JSON authentication (`email`, `password`) |
| **Refresh Token** | `/api/v1/auth/refresh` | `POST` | Client Interceptor | Background JWT refresh when 401 occurs |
| **User Profile** | `/api/v1/auth/me` | `GET`, `PATCH` | `/account` | View & update user profile |
| **Dashboard** | `/api/v1/dashboard/` | `GET` | `/dashboard` | System totals & recent activity |
| **Startup List** | `/api/v1/startup-profile/` | `GET` | `/startups`, Layout | List authenticated user's startups |
| **Startup Create**| `/api/v1/startup-profile/` | `POST` | `/startups/new` | Step 1 of creation wizard |
| **Startup Detail**| `/api/v1/startup-profile/{id}`| `GET`, `PATCH`| `/startups/:id`, `/edit`| Retrieve and update entity profile |
| **Startup Delete**| `/api/v1/startup-profile/{id}`| `DELETE` | `/startups`, `/startups/:id` | Permanent entity deletion |
| **Financials** | `/api/v1/financial-information/{id}` | `GET`, `PUT` | Wizard, Detail, Edit | Upsert initial capital, revenue, burn |
| **Team** | `/api/v1/team-information/{id}` | `GET`, `PUT` | Wizard, Detail, Edit | Upsert founders, employee count, skills |
| **Location** | `/api/v1/business-location/{id}` | `GET`, `PUT` | Wizard, Detail, Edit | Upsert address, city, state, country |
| **Land** | `/api/v1/land-details/{id}` | `GET`, `PUT` | Wizard, Detail, Edit | Upsert conditional physical premises |
| **Run Prediction**| `/api/v1/predictions/run/{id}` | `POST` | `/startups/:id/predictions` | Run deterministic simulation engine |
| **List Predictions**| `/api/v1/predictions/{id}` | `GET` | `/startups/:id/predictions` | Full historical prediction logs |
| **Latest Prediction**| `/api/v1/predictions/{id}/latest`| `GET` | Dashboard, Detail, Predictions | Retrieve most recent prediction result |
| **AI Suggestions**| `/api/v1/ai-suggestions/generate/{id}`| `POST` | `/startups/:id/suggestions` | Derive strategic advice from prediction |
| **List Suggestions**| `/api/v1/ai-suggestions/{id}` | `GET` | `/startups/:id/suggestions` | Retrieve active recommendations |
| **Delete Suggestion**| `/api/v1/ai-suggestions/{id}` | `DELETE` | `/startups/:id/suggestions` | Dismiss single recommendation |
| **Generate Report**| `/api/v1/reports/generate/{id}` | `POST` | `/startups/:id/reports` | Compile ReportLab PDF document |
| **List Reports** | `/api/v1/reports/{id}` | `GET` | `/startups/:id/reports` | Archive of compiled PDF reports |
| **Download PDF** | `/api/v1/reports/download/{id}` | `GET` | `/startups/:id/reports` | Authenticated blob download of PDF |

---

## 7. Common Integration Diagnostics

1. **`CORS Request Blocked` / `Network Error`**:
   - Verify the backend server is running at `http://127.0.0.1:8000`.
   - Check `VITE_API_BASE_URL` in `.env`.
   - Verify `cors_origins` in the FastAPI configuration allows the frontend origin. (Backend `allow_origin_regex` automatically permits `http://localhost:*` and `http://127.0.0.1:*`).
2. **`401 Unauthorized` on report downloads**:
   - The report download endpoint requires bearer authentication. The frontend uses `reportApi.downloadPdf` which attaches `Authorization: Bearer <token>` to fetch the blob rather than relying on unauthenticated browser redirects.
3. **`400 No prediction available` on AI suggestions**:
   - The backend rule engine requires a prediction record before suggestions can be generated. Run a prediction on `/startups/:id/predictions` first.
4. **Database Connection Errors**:
   - If the backend returns `500 Internal Server Error` with PostgreSQL connection errors, verify your local PostgreSQL service is running and credentials in `backend/.env` match your local PostgreSQL configuration.
