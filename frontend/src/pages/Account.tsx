import { AccountView } from '@neondatabase/neon-js/auth/react/ui';
import { useParams } from 'react-router-dom';

function Account() {
  const { view } = useParams();
  return (
    <div className="flex justify-center items-center min-h-screen">
      <AccountView pathname={view} />
    </div>
  );
}

export default Account;
