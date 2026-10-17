package com.indic.voice.presets

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.indic.voice.R

class ExampleScriptsBottomSheet(
    private val onScriptSelected: (String) -> Unit
) : BottomSheetDialogFragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.bottom_sheet_example_scripts, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        view.findViewById<View>(R.id.btnCloseScripts).setOnClickListener {
            dismiss()
        }

        val recyclerView = view.findViewById<RecyclerView>(R.id.rvExampleScripts)
        recyclerView.layoutManager = LinearLayoutManager(requireContext())
        recyclerView.adapter = ExampleScriptsAdapter(PresetData.exampleTranscripts) { script ->
            onScriptSelected(script.text)
            dismiss()
        }
    }

    private class ExampleScriptsAdapter(
        private val items: List<ExampleTranscript>,
        private val onClick: (ExampleTranscript) -> Unit
    ) : RecyclerView.Adapter<ExampleScriptsAdapter.ViewHolder>() {

        class ViewHolder(val view: View) : RecyclerView.ViewHolder(view) {
            val title: TextView = view.findViewById(R.id.tvScriptTitle)
            val badge: TextView = view.findViewById(R.id.tvScriptBadge)
            val text: TextView = view.findViewById(R.id.tvScriptText)
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_example_script, parent, false)
            return ViewHolder(view)
        }

        override fun onBindViewHolder(holder: ViewHolder, position: Int) {
            val item = items[position]
            holder.title.text = item.title
            holder.badge.text = item.advantageBadge
            holder.text.text = item.text

            holder.view.setOnClickListener {
                onClick(item)
            }
        }

        override fun getItemCount(): Int = items.size
    }
}
