import React from 'react';
import { Text, Stack, VStack, Heading, Box } from '@chakra-ui/react';

import Form from './components/Form';
import Header from './components/Header';

export default function App() {

  return (
    <div>

      <VStack p={5} spacing="20" mb={20}>

        <Header />

        <Stack direction={['column', 'row']} spacing={4}>

              <VStack spacing={3}>
                <Heading as="h2" size="lg">
                    Your assistant at finger tips
                </Heading>
                <Text color="gray.500" align="center" maxW="80ch" letterSpacing="wide">
                  Sit back and relax while YT assistant redy to serve you all the time including deep 
                  search and notification on personal preference and much more
                  </Text>
              </VStack>
              
        </Stack>

        <Form />
      </VStack>

    </div>
  )
}
