// import { useState } from 'react'
// import reactLogo from './assets/react.svg'
// import viteLogo from '/vite.svg'
// import './App.css'

import DashboardContainer from "./pages/DashboardContainer";
import AllBillboard from "./pages/AllBilboard";
import ReportList from "./pages/ReportList";
import BillboardReport from "./pages/BillboardReport";
// import AllBillboard from "./pages/AllBillboard";
import './index.css'
import Sidebar from "./components/SideBar";
import { Routes, Route } from "react-router-dom";
import BillboardDetail from "./pages/BillboardDetail";


function App() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-grow p-8">
        <Routes>
          <Route path="/overview" element={<DashboardContainer />} />
          <Route path="/all-billboard" element={<AllBillboard />} />
          <Route path="report" element={<ReportList />} />
          <Route path="report/:billboardName" element={<BillboardReport />} />
          <Route path="all-billboard/:id" element={<BillboardDetail />} />
          {/* Add additional routes as needed */}
        </Routes>
      </div>
    </div>
  );
}

export default App
