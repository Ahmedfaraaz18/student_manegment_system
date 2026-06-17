export default function RecentAnnouncements() {
  const announcements = [
    "Midterm exam schedule published",
    "Library extended hours this week",
    "Project submission deadline reminder",
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">Recent Announcements</h2>
      <ul className="space-y-3 text-sm text-gray-700">
        {announcements.map((item) => (
          <li key={item} className="border-b border-gray-100 pb-2">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
