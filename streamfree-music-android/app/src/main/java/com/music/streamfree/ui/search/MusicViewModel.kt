package com.music.streamfree.ui.search

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import com.music.streamfree.data.ExtractorRepository
import com.music.streamfree.domain.Track
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class MusicViewModel @Inject constructor(
    private val repository: ExtractorRepository,
    private val player: ExoPlayer
) : ViewModel() {

    private val _searchResults = MutableStateFlow<List<Track>>(emptyList())
    val searchResults: StateFlow<List<Track>> = _searchResults

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    fun search(query: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _searchResults.value = repository.search(query)
            } catch (e: Exception) {
                // Gestion d'erreur
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun playTrack(track: Track) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val streamUrl = repository.getStreamUrl(track.id)
                streamUrl?.let { url ->
                    val mediaItem = MediaItem.fromUri(url)
                    player.setMediaItem(mediaItem)
                    player.prepare()
                    player.play()
                }
            } catch (e: Exception) {
                // Gestion d'erreur
            } finally {
                _isLoading.value = false
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        // Libération des ressources si besoin, bien que le service gère ExoPlayer
    }
}
