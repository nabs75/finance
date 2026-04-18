import { getPosts } from "@/lib/wordpress";

export default async function NewsTicker() {
  const posts = await getPosts();
  const titles = posts.map((p: any) => p.title.rendered).join(" • ");

  return (
    <div class="bg-accent/10 border-b border-accent/20 py-2 overflow-hidden whitespace-nowrap">
      <div class="container mx-auto px-4 flex items-center">
        <span class="bg-accent text-white text-[10px] font-bold px-2 py-0.5 rounded mr-4 z-10">EN DIRECT</span>
        <div class="relative flex overflow-x-hidden w-full">
          <div class="animate-ticker inline-block text-sm font-medium text-accent uppercase tracking-wider">
            {titles || "Chargement des dernières actualités mondiales..."}
          </div>
        </div>
      </div>
    </div>
  );
}