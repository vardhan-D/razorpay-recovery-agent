import {
  BrowserRouter,
  Route,
  Routes,
} from "react-router-dom"

import Dashboard from "./pages/Dashboard"
import RecoveryCaseDetail from "./pages/RecoveryCaseDetail"


function App() {
  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Dashboard />}
        />

        <Route
          path="/cases/:caseId"
          element={
            <RecoveryCaseDetail />
          }
        />

      </Routes>

    </BrowserRouter>
  )
}


export default App