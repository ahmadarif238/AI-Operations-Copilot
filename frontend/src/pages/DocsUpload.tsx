import { useState } from 'react'
import { Upload, Check, AlertCircle } from 'lucide-react'

export default function DocsUpload() {
    const [files, setFiles] = useState<FileList | null>(null)
    const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle')
    const [msg, setMsg] = useState('')

    const handleUpload = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!files || files.length === 0) return

        setStatus('uploading')
        const formData = new FormData()
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i])
        }

        // Optional metadata
        formData.append('department', 'General')
        formData.append('category', 'SOP')

        try {
            const res = await fetch('http://localhost:8000/api/v1/docs/upload', {
                method: 'POST',
                body: formData
            })
            if (!res.ok) throw new Error('Upload failed')
            setStatus('success')
            setMsg(`Successfully uploaded ${files.length} documents.`)
            setFiles(null)
        } catch (err) {
            setStatus('error')
            setMsg('Failed to upload documents.')
        }
    }

    return (
        <div className="p-8 max-w-3xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Knowledge Base</h1>
            <p className="text-gray-500 mb-8">Upload PDF or DOCX policies to index them for the Copilot.</p>

            <div className="bg-white p-8 rounded-xl border border-gray-200 shadow-sm text-center">
                <form onSubmit={handleUpload} className="flex flex-col items-center gap-6">
                    <div className="w-full h-48 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors relative">
                        <input
                            type="file"
                            multiple
                            onChange={e => setFiles(e.target.files)}
                            className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                        <div className="p-4 bg-white rounded-full shadow-sm mb-3">
                            <Upload className="text-blue-600" size={24} />
                        </div>
                        <p className="font-medium text-gray-700">Click or Drag files to upload</p>
                        <p className="text-sm text-gray-500 mt-1">PDF, DOCX, TXT supported</p>
                    </div>

                    {files && files.length > 0 && (
                        <div className="w-full text-left bg-blue-50 p-3 rounded-lg text-sm text-blue-700 font-medium">
                            {files.length} file(s) selected
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={status === 'uploading' || !files}
                        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {status === 'uploading' ? 'Indexing...' : 'Start Upload & Index'}
                    </button>
                </form>

                {status === 'success' && (
                    <div className="mt-6 p-4 bg-green-50 text-green-700 rounded-lg flex items-center justify-center gap-2">
                        <Check size={20} /> {msg}
                    </div>
                )}

                {status === 'error' && (
                    <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-lg flex items-center justify-center gap-2">
                        <AlertCircle size={20} /> {msg}
                    </div>
                )}
            </div>
        </div>
    )
}
