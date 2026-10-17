package com.indic.voice.presets

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.google.android.material.chip.ChipGroup
import com.indic.voice.R

class QuickIdeasBottomSheet(
    private val onIdeaSelected: (String) -> Unit
) : BottomSheetDialogFragment() {

    private lateinit var adapter: QuickIdeasAdapter
    private var selectedLanguage: IdeaLanguage = IdeaLanguage.ALL

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.bottom_sheet_quick_ideas, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<View>(R.id.btnCloseIdeas).setOnClickListener {
            dismiss()
        }

        val chipGroup = view.findViewById<ChipGroup>(R.id.cgLanguageFilter)
        chipGroup.setOnCheckedStateChangeListener { _, checkedIds ->
            selectedLanguage = when {
                checkedIds.contains(R.id.chipEn) -> IdeaLanguage.ENGLISH
                checkedIds.contains(R.id.chipHi) -> IdeaLanguage.HINDI
                checkedIds.contains(R.id.chipTe) -> IdeaLanguage.TELUGU
                checkedIds.contains(R.id.chipTa) -> IdeaLanguage.TAMIL
                else -> IdeaLanguage.ALL
            }
            updateFilteredList()
        }

        val recyclerView = view.findViewById<RecyclerView>(R.id.rvQuickIdeas)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        adapter = QuickIdeasAdapter { idea ->
            onIdeaSelected(idea.text)
            dismiss()
        }
        recyclerView.adapter = adapter

        updateFilteredList()
    }

    private fun updateFilteredList() {
        val filtered = PresetData.quickIdeas.filter {
            selectedLanguage == IdeaLanguage.ALL || it.language == selectedLanguage
        }
        adapter.setItems(filtered)
    }

    private class QuickIdeasAdapter(
        private val onClick: (QuickIdea) -> Unit
    ) : RecyclerView.Adapter<QuickIdeasAdapter.ViewHolder>() {

        private val items = mutableListOf<QuickIdea>()

        fun setItems(newItems: List<QuickIdea>) {
            items.clear()
            items.addAll(newItems)
            notifyDataSetChanged()
        }

        class ViewHolder(val view: View) : RecyclerView.ViewHolder(view) {
            val language: TextView = view.findViewById(R.id.tvIdeaLanguage)
            val length: TextView = view.findViewById(R.id.tvIdeaLength)
            val text: TextView = view.findViewById(R.id.tvIdeaText)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_quick_idea, parent, false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val item = items[position]
            holder.language.text = item.language.displayName
            holder.length.text = when (item.section) {
                IdeaSection.SHORT -> "1 sentence"
                IdeaSection.MEDIUM -> "2–3 sentences"
                IdeaSection.LONG -> "Paragraph"
            }
            holder.text.text = item.text

            holder.view.setOnClickListener {
                onClick(item)
            }
        }

        override fun getItemCount(): Int = items.size
    }
}
