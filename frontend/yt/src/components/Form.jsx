import React, { useState, useRef } from 'react'
import { FormControl, FormLabel, Input, Button, Kbd, Stack } from '@chakra-ui/react';
// import "@pathofdev/react-tag-input/build/index.css";
// import ReactTagInput from "@pathofdev/react-tag-input";

import './Form.css';


/* 
TODO- 
1. tag input
  2. responsive
  3. size of box 
  4. color of tag box
  5. clear all button


*/

export default function Form() {

  const [tags, setTags] = useState(["example tag"]);
  const linkRef = useRef();

  const submitHandler = async (e) => {
    e.preventDefault();
    const video_link = linkRef.current.value;

    linkRef.current.value = "";

    const response = await fetch("http://localhost:5000/subscribe", {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({tags: tags, video_link: video_link}) // body data type must match "Content-Type" header
    });
    const data = await response.json(); 
    console.log("data received")
    console.log(data)
  }

  return (
      <form onSubmit={submitHandler}>
        <Stack spacing={8} borderWidth='1px' borderRadius='lg' p={10}>
          <FormControl isRequired>
              <FormLabel htmlFor='video-link'>Video Link</FormLabel>
              <Input id='video-link' placeholder='video link' ref={linkRef} name="video_link" />
          </FormControl>
          <FormControl isRequired width="lg">
            <FormLabel htmlFor='tag'>Tag</FormLabel>
              <ReactTagInput
                addedClass="modify"
                className="modify"
                tags={tags} 
                onChange={(newTags) => setTags(newTags)}
                name="tags"
              />
          </FormControl>
          <Button colorScheme="red" type="submit">Watch</Button>
        </Stack>
      </form>
  )
}
