/**
 * App Component
 *
 * Root application component with routing and DI providers.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import { TimelinePage } from "@/components/pages/TimelinePage";
import { LoggerProvider } from "@/components/LoggerContext";
import { sentryLogger } from "@/adapter/infra/sentryLogger";
import { DebugPage } from "./components/pages/debugPage";
import { FieldList } from "./components/pages/FieldList";
import { AtmosphereBackground } from "./components/atoms/AtmosphereBackground";
import { Toaster } from "@/components/ui/sonner";

function App() {
  return (
    <LoggerProvider logger={sentryLogger}>
      <AtmosphereBackground />
      <BrowserRouter>
        <Routes>
          {/* Landing: Field Selection */}
          <Route path="/" element={<FieldList />} />

          {/* Redirect legacy /timeline to root for field selection */}
          <Route path="/timeline" element={<Navigate to="/" replace />} />

          {/* Field Routes */}
          <Route path="/field/:fieldId" element={<TimelinePage />} />
          <Route
            path="/field/:fieldId/bonfire/:bonfireId"
            element={<TimelinePage />}
          />

          <Route path="/health" element={<HealthCheckPage />} />
          <Route path="/debug" element={<DebugPage />} />

          {/* Catch-all redirect to root */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
      <Toaster position="bottom-center" />
    </LoggerProvider>
  );
}

export default App;
