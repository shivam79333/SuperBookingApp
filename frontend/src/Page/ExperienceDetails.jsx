import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api/api";

export function ExperienceDetails() {
  const { id } = useParams();

  useEffect(() => {
    getItem();
  }, []);

  const getItem = () => {
    api
      .get(`/api/experience/${id}`)
      .then((res) => res.data)
      .then((data) => {
        console.log(data);
      })
      .catch((err) => alert(err));
  };
  return (
    <div>
      <div></div>
    </div>
  );
}
