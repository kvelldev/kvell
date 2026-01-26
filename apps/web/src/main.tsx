/**
 * Application Entry Point
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import ReactGA from "react-ga4";

ReactGA.initialize("G-78SVE5V35G");
ReactGA.send({ hitType: "pageview", page: globalThis.location.pathname });

const rootElement = document.querySelector("#root");

if (!rootElement) {
  throw new Error("Root element not found");
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
