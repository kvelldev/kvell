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
import { AtmosphereBackground } from "./components/atoms/AtmosphereBackground";

function App() {
  return (
    <LoggerProvider logger={sentryLogger}>
      <AtmosphereBackground />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/debug" replace />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/health" element={<HealthCheckPage />} />
          <Route path="/debug" element={<DebugPage />} />
        </Routes>
      </BrowserRouter>
    </LoggerProvider>
  );
}

export default App;
