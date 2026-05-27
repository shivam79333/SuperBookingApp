import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/api";
import ExperienceCard from "../components/ExperienceCard";
import Loading from "../components/Loading";

export default function LocationPage() {
  const { id } = useParams();
  const [location, setLocation] = useState(null);
  const [experiences, setExperiences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError("");
      try {
        const [locationRes, allExperiencesRes] = await Promise.all([
          api.get(`/api/location/${id}`),
          api.get("/api/experiences/"),
        ]);
        const locationData = locationRes.data || null;
        const allExperiences = Array.isArray(allExperiencesRes.data)
          ? allExperiencesRes.data
          : Array.isArray(allExperiencesRes.data?.results)
            ? allExperiencesRes.data.results
            : [];

        let filteredExperiences = allExperiences;
        if (locationData?.name) {
          const normalizedLocationName = locationData.name.trim().toLowerCase();
          filteredExperiences = allExperiences.filter(
            (exp) =>
              String(exp?.location || "")
                .trim()
                .toLowerCase() === normalizedLocationName,
          );
        }

        setLocation(locationData);
        setExperiences(filteredExperiences);
      } catch (err) {
        setError(err?.message || "Failed to load location experiences.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  if (loading) return <Loading />;
  if (error) return <div className="body">Error: {error}</div>;

  return (
    <div className="body py-6">
      <h1
        className="text-xl sm:text-2xl lg:text-3xl font-semibold tracking-tight mb-6 pb-2 border-b"
        style={{
          color: "var(--md-sys-color-on-surface)",
          borderColor: "var(--md-sys-color-outline-variant)",
        }}
      >
        {location?.name || "Location"} Experiences
      </h1>

      {experiences.length === 0 ? (
        <p>No experiences found for this location.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {experiences.map((experience) => (
            <ExperienceCard key={experience.public_id} experience={experience} />
          ))}
        </div>
      )}
    </div>
  );
}
