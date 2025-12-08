/**
 * App Component
 *
 * Root application component with routing and DI providers.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";
import { SparkPostPage } from "@/components/pages/SparkPostPage";
import { TimelinePage } from "@/components/pages/TimelinePage";
import { LoggerProvider } from "@/components/LoggerContext";
import { sentryLogger } from "@/adapter/infra/sentryLogger";
import { DebugPage } from "./components/pages/debug";

function App() {
  return (
    <LoggerProvider logger={sentryLogger}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Navigate to="/debug" replace />} />
          <Route path="/timeline" element={<TimelinePage />} />
          <Route path="/spark" element={<SparkPostPage />} />
          <Route path="/health" element={<HealthCheckPage />} />
          <Route path="/debug" element={<DebugPage />} />
        </Routes>
      </BrowserRouter>
    </LoggerProvider>
  );
}

export default App;
