package com.music.streamfree.domain

data class Track(
    val id: String,
    val title: String,
    val artist: String,
    val thumbnailUrl: String,
    val streamUrl: String? = null
)
