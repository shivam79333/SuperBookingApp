import { useEffect, useState } from "react";
import { getExperiences } from "../api/api";
import ExperienceCard from "../components/ExperienceCard";

function Home() {
  const [experiences, setExperiences] = useState([]);

  useEffect(() => {
    getExperiences().then((res) => {
      setExperiences([res.data]);
    });
  }, []);

  return (
    <div className="home-page">
      <h1 className="home-page__title">Experiences</h1>

      <div className="experience-grid">
        {experiences.map((exp) => (
          <ExperienceCard key={exp.id} experience={exp} />
        ))}
      </div>
    </div>
  );
}

export default Home;
