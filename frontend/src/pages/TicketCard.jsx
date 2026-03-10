function TicketCard({title, price}) {
  return (
    <div className="border rounded-lg p-6 shadow">
      <h3 className="text-xl font-semibold">{title}</h3>

      <ul className="mt-3 text-gray-600">
        <li>✔ Entry to museum</li>
        <li>✔ Audio guide</li>
        <li>✔ Access to exhibitions</li>
      </ul>

      <p className="mt-4 font-bold">${price}</p>

      <button className="bg-red-500 text-white px-4 py-2 rounded mt-3">
        Check availability
      </button>
    </div>
  )
}

export default TicketCard