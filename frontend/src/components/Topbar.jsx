export default function Topbar() {
  const logout = () => {

    localStorage.removeItem("token");

    window.location.href = "/login";

  }

  return (
    <div className="bg-white shadow-sm px-6 py-4 flex justify-between items-center">

      <h2 className="text-lg font-semibold text-gray-700">
        Dashboard
      </h2>

      <div className="flex items-center gap-4">

        <span className="text-gray-600">Admin</span>

        <button
          onClick={logout}
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Logout
        </button>

      </div>

    </div>
  );
}
