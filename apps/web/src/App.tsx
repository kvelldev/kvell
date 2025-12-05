/**
 * App Component
 *
 * Root application component with routing and DI providers.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import { SparkPostPage } from "@/components/pages/SparkPostPage";
import { LoggerProvider } from "@/components/LoggerContext";
import { sentryLogger } from "@/adapter/infra/sentryLogger";

function App() {
  return (
    <LoggerProvider logger={sentryLogger}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/spark" replace />} />
          <Route path="/spark" element={<SparkPostPage />} />
          <Route path="/health" element={<HealthCheckPage />} />
        </Routes>
      </BrowserRouter>
    </LoggerProvider>
  );
}

export default App;
