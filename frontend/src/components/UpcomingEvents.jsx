export default function UpcomingEvents() {
  const events = [
    { title: "Hackathon 2026", date: "Mar 18" },
    { title: "Campus Placement Drive", date: "Mar 24" },
    { title: "Tech Symposium", date: "Apr 02" },
  ];

  return (
    <div className="bg-white p-6 rounded-xl shadow">
      <h2 className="text-lg font-semibold mb-4">Upcoming Events</h2>
      <ul className="space-y-3 text-sm text-gray-700">
        {events.map((event) => (
          <li key={event.title} className="flex justify-between border-b border-gray-100 pb-2">
            <span>{event.title}</span>
            <span className="text-gray-500">{event.date}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
