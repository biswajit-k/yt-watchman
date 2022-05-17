import React from 'react';
import {ChakraProvider} from '@chakra-ui/react';
import ReactDOM from 'react-dom';

import './index.css';
import App from './App';
import theme from './theme/theme';
import '@fontsource/inter';

ReactDOM.render(

    <ChakraProvider theme={theme}>
        <App />
    </ChakraProvider>
    ,document.getElementById('root'));

