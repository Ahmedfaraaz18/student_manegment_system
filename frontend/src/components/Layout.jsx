import AIAssistant from "./AIAssistant"
import Navbar from "./Navbar"
import Sidebar from "./Sidebar"

function Layout({ children }) {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <main className="page-content">{children}</main>
        <AIAssistant />
      </div>
    </div>
  )
}

export default Layout
