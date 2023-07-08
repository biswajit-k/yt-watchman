import { useEffect, useState } from "react";


// custom hook to provide user image
// TODO: change place of storage of user images
const useImage = (user_id) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [image, setImage] = useState(null);
  useEffect(() => {
    const fetchImage = async () => {
      try {
        const response = await import(
          /* @vite-ignore */                  
          `./../../data/profile/guest.jpg`
          // rollup import tracking issue
        );
        setImage(response.default);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchImage();
  }, [user_id]);

  return {
    loading,
    error,
    image,
  };
};

export default useImage;
