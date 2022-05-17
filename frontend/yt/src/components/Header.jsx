import React from 'react'
import { Flex, HStack, Spacer, IconButton, useColorMode, Heading, Text } from '@chakra-ui/react';
import { FaSun, FaMoon, FaGithub } from 'react-icons/fa';

export default function Header() {

  const { colorMode, toggleColorMode } = useColorMode();
  const isDark = colorMode === "dark";
  
  return (
    <Flex w="100%" align="baseline" mx="8">
          <Heading size="md" fontWeight="semibold">YT <Text display="inline-block" color="red.500">Watchman</Text></Heading>
          <Spacer />
          <HStack shouldWrapChildren spacing={1}>
            <IconButton icon={<FaGithub />} isRound="true" />
            <IconButton ml={3} icon={ isDark ? <FaSun /> : <FaMoon />} isRound="true" onClick={toggleColorMode} />
          </HStack>
    </Flex>
  )
}
