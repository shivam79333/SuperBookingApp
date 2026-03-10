import { Link } from "react-router-dom";

function ExperienceCard({ experience }) {
  return (
    <div className="card">

      <img src={experience.image_url} width="200" />

      <h3>{experience.name}</h3>

      <p>{experience.location}</p>

      <p>Base Price: ${experience.entry_fee_base}</p>

      <Link to={`/experience/${experience.id}`}>
        View Details
      </Link>

    </div>
  );
}

export default ExperienceCard;