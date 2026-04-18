export default function AdBanner() {
    return (
        <div class="col-span-full bg-accent/5 border border-accent/20 rounded-3xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 my-8">
            <div class="text-center md:text-left">
                <span class="text-[10px] font-bold text-accent uppercase tracking-widest bg-accent/10 px-2 py-1 rounded mb-4 inline-block">Sponsorisé</span>
                <h3 class="text-2xl font-bold mb-2">Propulsez votre marque ici</h3>
                <p class="text-gray-400">Atteignez une audience mondiale avec nos formats publicitaires natifs.</p>
            </div>
            <button class="bg-white text-black font-bold px-8 py-4 rounded-2xl hover:bg-gray-200 transition-all whitespace-nowrap">
                Nous contacter
            </button>
        </div>
    );
}