/**
 * App Component
 *
 * Root application component with routing.
 */

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { HealthCheckPage } from "@/components/pages/HealthCheckPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/health" replace />} />
        <Route path="/health" element={<HealthCheckPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
