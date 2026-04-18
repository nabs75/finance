import { getPosts } from "@/lib/wordpress";
import AdBanner from "@/components/AdBanner";

export default async function Home() {
  const posts = await getPosts();

  return (
    <main class="container mx-auto px-4 py-12">
      <div class="mb-12">
        <h2 class="text-4xl font-extrabold mb-2 tracking-tight">À la une</h2>
        <div class="h-1 w-20 bg-accent"></div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {posts.length > 0 ? (
          posts.map((post: any) => (
            <article key={post.id} class="group cursor-pointer">
              <div class="aspect-video bg-card border border-white/5 rounded-2xl mb-4 overflow-hidden transition-all group-hover:border-accent/50">
                {post._embedded?.['wp:featuredmedia'] ? (
                  <img
                    src={post._embedded['wp:featuredmedia'][0].source_url}
                    alt={post.title.rendered}
                    class="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500"
                  />
                ) : (
                  <div class="w-full h-full flex items-center justify-center text-gray-700">Pas d'image</div>
                )}
              </div>
              <h3 class="text-xl font-bold mb-3 leading-snug group-hover:text-accent transition-colors"
                  dangerouslySetInnerHTML={{ __html: post.title.rendered }}>
              </h3>
              <div class="text-gray-400 text-sm line-clamp-3 mb-4"
                   dangerouslySetInnerHTML={{ __html: post.excerpt.rendered }}>
              </div>
              <div class="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-gray-500">
                <span>{new Date(post.date).toLocaleDateString('fr-FR')}</span>
                <span class="w-1 h-1 bg-gray-700 rounded-full"></span>
                <span class="text-accent">Dépêche IA</span>
              </div>
            </article>
          ))
        ) : (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} class="animate-pulse">
              <div class="aspect-video bg-card rounded-2xl mb-4"></div>
              <div class="h-6 bg-card rounded w-3/4 mb-2"></div>
              <div class="h-4 bg-card rounded w-full mb-1"></div>
              <div class="h-4 bg-card rounded w-2/3"></div>
            </div>
          ))
        )}
        {posts.length > 3 && <AdBanner />}
      </div>
    </main>
  );
}