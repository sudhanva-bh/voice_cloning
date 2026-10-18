package com.indic.voice.history

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.LinearLayout
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.indic.voice.R
import com.indic.voice.SeekableAudioPlayerView

class HistoryAdapter(
    private val onExport: (GeneratedClipItem) -> Unit,
    private val onShare: (GeneratedClipItem) -> Unit,
    private val onDelete: (GeneratedClipItem) -> Unit
) : RecyclerView.Adapter<HistoryAdapter.ViewHolder>() {

    private val items = mutableListOf<GeneratedClipItem>()

    fun setItems(newItems: List<GeneratedClipItem>) {
        items.clear()
        items.addAll(newItems)
        notifyDataSetChanged()
    }

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tvClipTitle)
        val ibShare: ImageButton = view.findViewById(R.id.ibShareClip)
        val ibExport: ImageButton = view.findViewById(R.id.ibExportClip)
        val ibDelete: ImageButton = view.findViewById(R.id.ibDeleteClip)
        val llBadges: LinearLayout = view.findViewById(R.id.llClipBadges)
        val tvRtf: TextView = view.findViewById(R.id.tvClipRtf)
        val tvRss: TextView = view.findViewById(R.id.tvClipRss)
        val player: SeekableAudioPlayerView = view.findViewById(R.id.playerClipAudio)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_history_clip, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val item = items[position]
        holder.tvTitle.text = item.displayTitle

        val hasRtf = !item.rtf.isNullOrEmpty()
        val hasRss = !item.rssMB.isNullOrEmpty()

        if (hasRtf || hasRss) {
            holder.llBadges.visibility = View.VISIBLE
            if (hasRtf) {
                holder.tvRtf.visibility = View.VISIBLE
                holder.tvRtf.text = "RTF: ${item.rtf}x"
            } else {
                holder.tvRtf.visibility = View.GONE
            }

            if (hasRss) {
                holder.tvRss.visibility = View.VISIBLE
                holder.tvRss.text = "Memory: ${item.rssMB} MB"
            } else {
                holder.tvRss.visibility = View.GONE
            }
        } else {
            holder.llBadges.visibility = View.GONE
        }

        holder.player.setAudioPath(item.file.absolutePath)

        holder.ibShare.setOnClickListener {
            onShare(item)
        }

        holder.ibExport.setOnClickListener {
            onExport(item)
        }

        holder.ibDelete.setOnClickListener {
            holder.player.pause()
            onDelete(item)
        }
    }

    override fun onViewRecycled(holder: ViewHolder) {
        super.onViewRecycled(holder)
        holder.player.pause()
    }

    override fun getItemCount(): Int = items.size
}
