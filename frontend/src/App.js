import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import ReactionInput from "./pages/ReactionInput";
import Candidates from "./pages/Candidates";
import Feedback from "./pages/Feedback";
import History from "./pages/History";
import "./styles.css";

export default function App() {
  const [reaction, setReaction] = useState("");

  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<ReactionInput setReaction={setReaction} />} />
        <Route path="/candidates" element={<Candidates reaction={reaction} />} />
        <Route path="/feedback" element={<Feedback reaction={reaction} />} />
        <Route path="/history" element={<History reaction={reaction} />} />
      </Routes>
    </BrowserRouter>
  );
}