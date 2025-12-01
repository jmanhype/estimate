/**
 * ProjectsPage - List and manage user projects
 */

export function ProjectsPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="flex-1 min-w-0">
            <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
              My Projects
            </h2>
          </div>
          <div className="mt-4 flex md:mt-0 md:ml-4">
            <a
              href="/projects/new"
              className="ml-3 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              New Project
            </a>
          </div>
        </div>
        <div className="mt-8">
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <p className="px-6 py-4 text-gray-500">
              No projects yet. Create your first project to get started!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
