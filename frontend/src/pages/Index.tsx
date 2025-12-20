import BenchmarkCard from "@/components/BenchmarkCard";
import { authClient } from "@/lib/auth";

const Index = () => {
  return (
    <BenchmarkCard onLogout={() => authClient.signOut()} />
  );
};

export default Index;
