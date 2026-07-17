import Home from "./pages/Home.jsx";
import Course from "./pages/Course.jsx";

export default function App() {
  const m = window.location.pathname.match(/^\/c\/([^/]+)/);
  if (m) return <Course slug={m[1]} />;
  return <Home />;
}
