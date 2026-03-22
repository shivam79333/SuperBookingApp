import { useState } from "react";
import { Link } from "react-router-dom";

function ExperienceCard({ experience }) {
  const images = String(experience.image_url || "")
    .split(",")
    .map((url) => url.trim())
    .filter(Boolean);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const showPrevImage = (event) => {
    event.preventDefault();
    event.stopPropagation();
    setCurrentImageIndex((prev) =>
      prev === 0 ? images.length - 1 : prev - 1
    );
  };

  const showNextImage = (event) => {
    event.preventDefault();

    setCurrentImageIndex((prev) =>
      prev === images.length - 1 ? 0 : prev + 1
    );
  };

  return (
    <Link to={`/experience/${experience.id}`} className="experience-card">
      <div className="experience-card__image-wrap">
        {images.length > 1 && (
          <>
            <button
              type="button"
              className="experience-card__arrow experience-card__arrow--left"
              onClick={showPrevImage}
            >
              ‹
            </button>
            <button
              type="button"
              className="experience-card__arrow experience-card__arrow--right"
              onClick={showNextImage}
            >
              ›
            </button>
          </>
        )}
        <img
          src={images[currentImageIndex] || experience.image_url}
          alt={experience.name}
          className="experience-card__image"
        />
      </div>

      <div className="experience-card__meta">
        <p className="experience-card__location">{experience.location}</p>
        <p className="experience-card__rating">★ 4.4 (4,689)</p>
      </div>

      <h3 className="experience-card__title">{experience.name}</h3>

      <p className="experience-card__price">₹{experience.entry_fee_base}</p>
    </Link>
  );
}

export default ExperienceCard;
