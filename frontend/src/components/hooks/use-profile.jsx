import React, {useEffect} from 'react'
import { useSelector, useDispatch } from 'react-redux';

import { userActions } from '../../store/user-store';


// custom hook to provide profile details
// fetches latest data if refresh is set to true
export default function useProfile(requester, refresh) {

  const user = useSelector((state) => state.user);
  const dispatch = useDispatch();

  useEffect(() => {
    if(refresh) {
      requester(
        {
          url: "/api/profile",
          body: {
            credentials: "include",
            mode: "cors",
          },
        },
        (profile) => {
          if (profile.id) {
            dispatch(userActions.loginUser(profile));
            return;
          }
          dispatch(userActions.logoutUser());
        }
      )
    }
  }, [refresh]);

  return user;
}
