/**
 * App Component
 *
 * Root application component with routing and DI providers.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import { LoggerProvider } from "@/usecase/ports/LoggerContext";
import { sentryLogger } from "@/adapter/infra/sentryLogger";

function App() {
  return (
    <LoggerProvider logger={sentryLogger}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/health" replace />} />
          <Route path="/health" element={<HealthCheckPage />} />
        </Routes>
      </BrowserRouter>
    </LoggerProvider>
  );
}

export default App;
