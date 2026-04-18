package com.music.streamfree.data

import com.music.streamfree.domain.Track
import org.schabi.newpipe.extractor.NewPipe
import org.schabi.newpipe.extractor.ServiceList
import org.schabi.newpipe.extractor.services.youtube.YoutubeService
import org.schabi.newpipe.extractor.stream.StreamInfo
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ExtractorRepository @Inject constructor() {

    init {
        // Initialisation de NewPipeExtractor (YouTube par défaut)
        NewPipe.init(null) 
    }

    suspend fun search(query: String): List<Track> {
        val service = ServiceList.YouTube
        val searchExtractor = service.searchExtractor(query)
        searchExtractor.fetchPage()
        
        return searchExtractor.initialPage.items.map { item ->
            Track(
                id = item.url,
                title = item.name,
                artist = item.uploaderName,
                thumbnailUrl = item.thumbnailUrl
            )
        }
    }

    suspend fun getStreamUrl(trackId: String): String? {
        val service = ServiceList.YouTube
        val streamInfo = StreamInfo.getInfo(service, trackId)
        
        // On récupère uniquement les flux audio (m4a ou webm)
        // Les flux audio directs ne contiennent aucune publicité vidéo
        return streamInfo.audioStreams
            .filter { it.format.name == "m4a" || it.format.name == "webm" }
            .maxByOrNull { it.bitrate }?.url
    }
}
